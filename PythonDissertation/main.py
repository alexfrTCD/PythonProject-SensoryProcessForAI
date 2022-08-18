"""
Created on Mon June  27 20:00:17 2022

@author: Alex
"""
import csv
import math
import sys
import time
import random

import keyboard  # using module keyboard
from datetime import datetime

import numpy as np
import cv2
import matplotlib.pyplot as plt
import pickle
from matplotlib import style

from CommunicationClass import CommunicationSocket
from BoardClass import Board
from AvatarClass import Avatar
from qLearning import qLearning

COLORS = {1: (25, 175, 0), 2: (0, 255, 0), 3: (0, 0, 255)}


class Game:
    def __init__(self):
        self.avatar = None
        self.board = None
        self.qlearning = qLearning()

        self.tempBefore = None
        self.glareBefore = None
        self.soundIntensityBefore = None
        self.temperature = None
        self.glare = None
        self.soundIntensity = None
        self.objectsDetected = []
        self.foundFoodReward = 1
        self.newHealth = None
        self.newHunger = None
        self.init = False

        self.fields = ['foodPos', 'obs', 'epsilon','timesAchieved','timesNotAchieved',"rotRight" , "rotLeft" , "rotUp" , "rotDown","up", "down", "left", "right",'idle', 'eat', 'temperature', 'glare', 'soundIntensity',
                       "rotRight_reward" , "rotLeft_reward" , "rotUp_reward" , "rotDown_reward",'left_reward', 'right_reward', 'down_reward', 'up_reward', 'idle_reward', 'eat_reward','health','hunger', 'position', 'rotation']
        self.rewardsField = ['foodPos','notAchieved','rewards', 'steps',]
        self.foodPosition = (-1, -1)
        self.pastFoodPosition = (-1,-1)
        self.distanceToFood = 0
        self.usingDrives = False

        self.healthToSave = 0
        self.hungerToSave = 0
        self.positionsFinished = []
        self.positionsFinished_aux = []
        self.positionsFinishedCounter = 10
        self.endingEpisode = False
        self.endingSearch = False
        self.rewardsAndSteps_AllEpisodes = {}

        self.episodeReward = 0
        self.randomPosition = True
    def runGame(self):
        obs = self.initCommunication()
        self.qlearning.initQtable()
        print("First observation:", obs)
        now = datetime.now()
        print(now)
        changingVariables = False

        while True:
            #if keyboard.is_pressed('e'):
            #    changingVariables = True

            if(changingVariables):
                value1 = input("Introduce new epsilon:\n")
                value2 = input("Please enter new epsilonDecay:\n")
                self.qlearning.epsilon = float(value1)
                self.qlearning.eps_decay = float(value2)
                changingVariables = False
            else:

                if(self.foodPosition not in list(self.rewardsAndSteps_AllEpisodes.keys())):
                    self.rewardsAndSteps_AllEpisodes[self.foodPosition] = {}
                    self.rewardsAndSteps_AllEpisodes[self.foodPosition]['rewards'] = []
                    self.rewardsAndSteps_AllEpisodes[self.foodPosition]['steps'] = []
                    self.rewardsAndSteps_AllEpisodes[self.foodPosition]['notAchieved'] = []
                # print("Avatar position: " , self.avatar.position , " with rotation: ",self.avatar.rotation   )
                # Deciding action -- q learning

                action = self.avatar.chooseAction(self.foodPosition, obs,  self.qlearning, self.board)

                #print("Action: ", action)
                #print("Observation received: " , obs)
                #action = self.avatar.random_movement(self.board)

                # Sending action
                #print("Q-Table actualized: ", self.qlearning.q_table)

                socks.connectionMovement(action)


                if action == "notAchieved":
                    if(self.rewardsAndSteps_AllEpisodes[self.foodPosition].get('notAchieved') == None):
                        listNotAchieved = [0]
                    else:
                        listNotAchieved =self.rewardsAndSteps_AllEpisodes[self.foodPosition]['notAchieved'] + [len(self.rewardsAndSteps_AllEpisodes[self.foodPosition]['rewards'])]
                    self.rewardsAndSteps_AllEpisodes[self.foodPosition]['notAchieved'] = listNotAchieved

                    self.qlearning.q_table[self.foodPosition]["notAchieved"] = self.qlearning.q_table[self.foodPosition].get('notAchieved') + 1
                    #print("new num notAchieved = ", self.qlearning.q_table[self.foodPosition].get('notAchieved'))
                    #self.writeData('test_output.csv')

                    totalSum = self.qlearning.q_table[self.foodPosition].get('notAchieved') + self.qlearning.q_table[self.foodPosition].get('achieved')
                    #totalSum = self.qlearning.q_table[self.foodPosition].get('achieved')
                    #print("new num achieved after eat: ", self.qlearning.q_table[self.foodPosition].get('achieved'))
                    #print("numEpisodes= ", totalSum)

                    #Writting the policy achieved every 10
                    if(totalSum % 10 == 0 and totalSum > self.positionsFinishedCounter-1 and  self.foodPosition not in self.positionsFinished_aux):
                        self.positionsFinished_aux.append(self.foodPosition)
                        if(len(self.positionsFinished_aux) > 10):
                            print("Inside where I want")
                            self.writeData('test_output'+str(self.positionsFinishedCounter)+'.csv')
                            self.writeRewardAndSteps('rewardAndSteps'+str(self.positionsFinishedCounter)+'.csv')
                            self.positionsFinishedCounter = self.positionsFinishedCounter + 10
                            self.positionsFinished_aux.clear()


                    if(totalSum > 100 and self.foodPosition not in self.positionsFinished):
                        print("time: ", datetime.now())
                        self.writeData('test_output'+str(self.positionsFinishedCounter)+'.csv')
                        self.writeRewardAndSteps('rewardAndSteps'+str(self.positionsFinishedCounter)+'.csv')
                        self.positionsFinished.append(self.foodPosition)
                        print("food positions done: ", self.positionsFinished, "with list length: ", len(self.positionsFinished))
                        #print("Actual positions: ", self.avatar.position)
                    if(len(self.positionsFinished) > 9):
                        print("Terminated at: ", datetime.now())
                        print("END GAME")
                        break

                    #print("Possible pos before not achieved: ", self.board.possiblePositions, "with length ", len(self.board.possiblePositions))

                    possible_row_cols_before = self.board.possiblePositions.copy()
                    self.board.possiblePositions.remove(self.avatar.position)

                    found = False
                    while (found == False):
                        newFoodPos = random.choice(self.board.possiblePositions)
                        if(newFoodPos != (-1,-1)):
                            print("new food pos: " , newFoodPos)
                            found = True


                    self.board.possiblePositions.append(self.avatar.position)

                    self.board.possiblePositions.remove(newFoodPos)
                    #print("Possible pos after not achieved 1: ", self.board.possiblePositions, "with length ", len(self.board.possiblePositions))

                    self.board.possiblePositions.append(self.foodPosition)

                    #print("Possible pos after if: ", self.board.possiblePositions, "with length ", len(self.board.possiblePositions))

                    socks.sendInfo(newFoodPos[0], "float")
                    socks.sendInfo(newFoodPos[1], "float")

                    #print("TOO MANY STEPS, ENDING EPISODE")
                    if(self.randomPosition == False):
                        self.avatar.position = (0,0)
                        self.avatar.rotation = (0,1)

                    obs = (self.avatar.position, self.avatar.rotation)
                    self.endingEpisode = True
                    self.foodPosition = newFoodPos
                    if(self.foodPosition not in list(self.rewardsAndSteps_AllEpisodes.keys())):
                        self.rewardsAndSteps_AllEpisodes[self.foodPosition] = {}
                        self.rewardsAndSteps_AllEpisodes[self.foodPosition]['rewards'] = []
                        self.rewardsAndSteps_AllEpisodes[self.foodPosition]['steps'] = []
                        self.rewardsAndSteps_AllEpisodes[self.foodPosition]['notAchieved'] = []

                else:

                    obsBefore = obs
                    self.tempBefore = self.temperature
                    self.glareBefore = self.glare
                    self.soundIntensityBefore = self.soundIntensity

                    #print("Action executed: ", action)
                    #print("Food pos", self.foodPosition)
                    #print("New position: ", self.avatar.position)
                    #print("New rotation: ", self.avatar.rotation)
                    # Receiving senses info after movement and new drives

                    self.temperature, self.glare, self.soundIntensity, self.objectsDetected = socks.receiveSensesInfo()

                    self.newHealth, self.newHunger = socks.receiveDrivesInfo()
                    if(self.usingDrives == True):
                        self.newHealth = int(self.newHealth)
                        self.newHunger = int(self.newHunger)

                    if(action == "eat"):
                        #Then we have to actualize possible positions
                        #print("inside eat possibility")
                        checkEat = self.avatar.check_eat_basic(self.foodPosition)
                        possible_row_cols_before  = self.board.possiblePositions.copy()
                        possible_row_cols = socks.actualizePossiblePositions()
                        #print("new possible pos: ", possible_row_cols)
                        self.board.possiblePositions = possible_row_cols
                        #print("Check Eat = " , checkEat)
                        if self.foodPosition in possible_row_cols:
                            print("THE AGENT HAS EATEN!!!")
                            #self.writeData('test_output.csv')
                            self.endingEpisode = True
                            totalSum = self.qlearning.q_table[self.foodPosition].get('notAchieved') + self.qlearning.q_table[self.foodPosition].get('achieved')
                            #totalSum = self.qlearning.q_table[self.foodPosition].get('achieved')
                            #print("new num achieved after eat: ", self.qlearning.q_table[self.foodPosition].get('achieved'))
                            #print("numEpisodes= ", totalSum)
                            if(self.qlearning.q_table[self.foodPosition].get('epsilon') > self.qlearning.minimumExpRate):

                                numEpisodes = self.qlearning.q_table[self.foodPosition].get('notAchieved') + self.qlearning.q_table[self.foodPosition].get('achieved')
                                #print("Num episodes for ", self.foodPosition)
                                self.qlearning.q_table[self.foodPosition]["epsilon"] = self.qlearning.minimumExpRate + ((self.qlearning.max_exploration_rate - self.qlearning.minimumExpRate) * math.exp(-self.qlearning.exploration_decay_rate * numEpisodes))
                                #print("new epsilon: ", self.qlearning.q_table[self.foodPosition]["epsilon"])


                            #Writting the policy achieved every 10
                            if(totalSum % 10 == 0 and totalSum > self.positionsFinishedCounter-1 and  self.foodPosition not in self.positionsFinished_aux):
                                self.positionsFinished_aux.append(self.foodPosition)
                                if(len(self.positionsFinished_aux) > 10):
                                    print("Inside where I want")
                                    self.writeData('test_output'+str(self.positionsFinishedCounter)+'.csv')
                                    self.writeRewardAndSteps('rewardAndSteps'+str(self.positionsFinishedCounter)+'.csv')
                                    self.positionsFinishedCounter = self.positionsFinishedCounter + 10
                                    self.positionsFinished_aux.clear()


                            if(totalSum > 100 and self.foodPosition not in self.positionsFinished):
                                self.writeData('test_output'+str(self.positionsFinishedCounter)+'.csv')
                                self.writeRewardAndSteps('rewardAndSteps'+str(self.positionsFinishedCounter)+'.csv')
                                self.positionsFinished.append(self.foodPosition)
                                #print("food positions done: ", self.positionsFinished, "with list length: ", len(self.positionsFinished))
                                #print("Actual positions: ", self.avatar.position)
                                if(len(self.positionsFinished) > 14 or (-1,-1) in self.positionsFinished):
                                    print("END GAME")
                                    print("Terminated at: ", datetime.now())
                                    break

                            #print("actualized positions: ", possible_row_cols)
                            self.qlearning.q_table[self.foodPosition]["achieved"] = self.qlearning.q_table[self.foodPosition].get('achieved') + 1


                    obs1 = self.temperature, self.glare, self.soundIntensity

                    #This should be add if we want to use the objects in the observation
                    #for element in self.objectsDetected:
                    #    obs1 = obs1+((element.objectType, element.position, element.distance))

                    obs2 = (self.avatar.position, self.avatar.rotation)
                    self.simplisizeDrives()
                    obs3 = (self.healthToSave, self.hungerToSave)
                    #obs3 = self.avatar.check_eat(self.board, self.objectsDetected)
                    if(self.foodPosition == (-1, -1)):
                        self.foodPosition =  self.avatar.check_pos(self.objectsDetected, self.avatar)
                        self.distanceToFood = abs(self.foodPosition[0] - self.avatar.position[0]) + abs(self.foodPosition[1] - self.avatar.position[1])

                    if self.usingDrives == True:

                        obs = obs2 + obs3
                        reward = self.calculateReward()
                    else:
                        obs = obs2
                        #print("food positiom before calculate reward: ", self.foodPosition)
                        #print("Actual step: ", self.avatar.totalSteps)
                        reward = self.calculateBasicReward()
                    #print("reward received: ", reward, "in position: ", self.avatar.position, " and rotation: ", self.avatar.rotation, "with health = ", self.avatar.health, "and hunger: ", self.avatar.hunger)
                    #print("Drives changed.  Last health =", self.lastHealth , "Actual health=",self.avatar.health )
                    #print("Last hunguer=",self.lastHunger, "Actual hunguer=", self.avatar.hunger)
                    #print("Reward: ", reward)

                    #Q-Learning
                    #print("foodPos: ", self.pastFoodPosition,"position and rotation;",obsBefore, "action made", action)
                    #print("Actual Position: ", self.avatar.position)
                    #print("sound intensity before: ", self.soundIntensityBefore)
                    self.qlearning.actualizeTable(self.pastFoodPosition,obsBefore,obs, action,reward, self.tempBefore, self.glareBefore, self.soundIntensityBefore)

                if(self.endingEpisode == True):
                    if(self.randomPosition == False):
                        self.avatar.position = (0,0)
                        self.avatar.rotation = (0,1)

                    obs = (self.avatar.position, self.avatar.rotation)
                    self.endingEpisode = False

                    #print("List of rewards ", "length: ", len(self.rewardsAndSteps_AllEpisodes[self.foodPosition]['rewards']) , "rewards: ", self.rewardsAndSteps_AllEpisodes[self.foodPosition]['rewards'])
                    #print("List of steps ", "length: ", len(self.rewardsAndSteps_AllEpisodes[self.foodPosition]['steps']) , "steps: ", self.rewardsAndSteps_AllEpisodes[self.foodPosition]['steps'])

                    if(self.rewardsAndSteps_AllEpisodes[self.foodPosition].get('rewards') == None):
                        rewardList = [self.episodeReward]

                    else:
                        rewardList = self.rewardsAndSteps_AllEpisodes[self.foodPosition]['rewards'] + [self.episodeReward]
                        #print("Inside else, adding new episode rewards")

                    self.rewardsAndSteps_AllEpisodes[self.foodPosition]['rewards'] = rewardList

                    if(self.rewardsAndSteps_AllEpisodes[self.foodPosition]['steps'] == None):
                        stepsList =  [self.avatar.totalSteps]

                    else:
                        stepsList =  self.rewardsAndSteps_AllEpisodes[self.foodPosition]['steps'] + [self.avatar.totalSteps]
                        #print("Inside else, adding new episode rewards")

                    #print("avatar total steps: ", self.avatar.totalSteps)

                    #print("List of after added episode", self.rewardsAndSteps_AllEpisodes.get(self.foodPosition))
                    self.rewardsAndSteps_AllEpisodes[self.foodPosition]['steps']  = stepsList

                    #self.findNewFoodPosition(possible_row_cols_before)
                    self.foodPosition = (-1,-1)

                    #print("ending episode reward: ", self.episodeReward)
                    self.episodeReward = 0

                    self.avatar.totalSteps = 0


                self.avatar.health = self.newHealth
                self.avatar.hunger = self.newHunger

                self.pastFoodPosition = self.foodPosition
                        #print("New position: ", self.avatar.position)
                        #print("New rotation: ", self.avatar.rotation)
                        #print("Q-Table actualized: ", self.qlearning.q_table)
            time.sleep(0.01)

    def initCommunication(self):

        self.avatar = Avatar(socks.initAvatarPosition(), socks.initAvatarRotation())
        rows, cols, possible_row_cols = socks.initBoard()
        #totalObjects = socks.initObjects()
        self.temperature, self.glare, self.soundIntensity, self.objectsDetected = socks.receiveSensesInfo()
        #obs1 = self.temperature, self.glare, self.soundIntensity
        self.board = Board(rows, cols, possible_row_cols)
        obs2 = self.avatar.position, self.avatar.rotation
        obs3 = (self.avatar.health, self.avatar.hunger)
        self.newHealth, self.newHunger = socks.receiveDrivesInfo()
        #for element in self.objectsDetected:
        #    obs1 = obs1 +((element.objectType, element.position, element.distance))
        self.foodPosition =  self.avatar.check_pos(self.objectsDetected, self.avatar)
        self.pastFoodPosition = self.foodPosition
        obs = obs2 + obs3
        return obs


    def calculateBasicReward(self):
        healthReward = (self.newHealth - self.avatar.health)
        # Only negative rewards by health drive
        #print("newHealth: " ,self.newHealth, "actualHealth: ", self.avatar.health)
        hungerReward = (self.avatar.hunger - self.newHunger)
        #print("newHunger: ", self.newHunger, "actualHunger: ", self.avatar.hunger)

        finalReward = hungerReward + healthReward
        self.foundFoodReward = 0

        if self.foodPosition != (-1,-1):
            self.episodeReward = self.episodeReward + finalReward
            #print("episode reward = " , self.episodeReward)
        return finalReward

    def calculateReward(self):

        if(self.newHealth > 0 and self.newHunger < 100):
            #print("newHealth", self.newHealth)
            #print("actual health: ", self.avatar.health)
            healthImportance = (2 ** (100 - self.avatar.health)) / (2**100)
            hungerImportance = (2 ** self.avatar.hunger) / (2**100)


            healthReward = ((self.newHealth - self.avatar.health) / 100) * healthImportance
            print("HealthReward ", healthReward)
            # Only negative rewards by health drive
            if (healthReward > 0):
                healthReward = 0

            hungerReward = ((self.avatar.hunger - self.newHunger) / 100) * hungerImportance
            print("HungerReward ", hungerReward)
            finalReward = hungerReward + healthReward

            self.episodeReward = self.episodeReward + finalReward
            return finalReward

        elif self.newHealth <= 0 :
            #self.timesDead = self.timesDead + 1
            self.avatar.health = 100
            self.newHealth = 100
            return -50
        elif self.newHunger >= 100:
            #self.timesDead = self.timesDead + 1
            self.avatar.hunger = 0
            self.newHunger = 0
            return -50

    def findNewFoodPosition(self, possiblePosBefore):
        founded = False
        counter = 0
        while not founded and counter < len(possiblePosBefore):
            if possiblePosBefore[counter] not in self.board.possiblePositions:
                founded = True
                self.foodPosition = possiblePosBefore[counter]
            else:
                counter = counter + 1
    def writeRewardAndSteps(self, fileName):
        try:
            with open(fileName, 'w', newline='') as file:
                writer = csv.DictWriter(file, self.rewardsField)
                writer.writeheader()
                #print("WRITING INFO")
                #print("keys: ", self.qlearning.q_table.keys())
                #print("items: ", self.qlearning.q_table.items())
                for key1,val1 in self.rewardsAndSteps_AllEpisodes.items():
                    #print('key1, ', key1)
                    #print("val1.get rewards ", val1.get('rewards') )
                    row = {'foodPos': key1,'notAchieved': val1.get('notAchieved') , 'rewards': val1.get('rewards')  , 'steps': self.rewardsAndSteps_AllEpisodes[key1].get('steps')}

                    #print("row",    row)

                    writer.writerow(row)
        except:
            print("SOMETHING WENT WRONG WRITING REWARDS")

    def writeData(self, fileName):

        try:

            with open(fileName, 'w', newline='') as f:
                w = csv.DictWriter(f, self.fields)
                w.writeheader()
                #print("WRITING INFO")
                #print("keys: ", self.qlearning.q_table.keys())
                #print("items: ", self.qlearning.q_table.items())
                for key1,val1 in self.qlearning.q_table.items():

                    #print("keys1: ", self.qlearning.q_table[key1].keys())
                    #print("items1: ", self.qlearning.q_table[key1].items())
                    for key2, val2 in self.qlearning.q_table[key1].items():
                        if(key2 != 'epsilon' and key2 != 'notAchieved' and key2 != 'achieved'):
                            #print("key2", key2)
                            #print("val2: ", val2)
                            row = {'foodPos': key1, 'obs': key2, 'epsilon': self.qlearning.q_table[key1].get('epsilon'), 'timesAchieved':self.qlearning.q_table[key1].get('achieved'), 'timesNotAchieved': self.qlearning.q_table[key1].get('notAchieved')}
                            #print("row: ", row)
                            #print("value: ", val2['everything'].items())
                            row.update(val2['everything'].items())
                            w.writerow(row)
        except:
            print("REMEMBER TO CLOSE THE FILE")


    def simplisizeDrives(self):
        if self.newHealth > 75:
            self.newHealth = 100
        elif(self.newHealth < 50 and self.newHealth >= 25):
            self.healthToSave = 50
        elif(self.newHealth <25 and self.newHealth >= 12):
            self.healthToSave  = 25
        elif(self.newHealth < 12 and self.newHealth >= 6):
            self.healthToSave  = 12
        elif(self.newHealth < 6 and self.newHealth >= 3):
            self.healthToSave  = 6
        elif(self.healthToSave  < 3 and self.newHealth >= 2):
            self.healthToSave = 3
        elif(self.healthToSave < 2 and self.newHealth >= 1):
            self.healthToSave = 2
        elif(self.newHealth > 1):
            self.healthToSave = 1

        if (self.newHunger < 25):
            self.hungerToSave = 0
        elif(self.newHunger > 50 and self.newHunger <= 75):
            self.hungerToSave = 50
        elif(self.newHunger >75 and self.newHunger <= 87):
            self.hungerToSave = 75
        elif(self.newHunger > 87 and self.newHunger <= 93):
            self.hungerToSave = 87
        elif(self.newHunger > 93 and self.newHunger <= 97):
            self.hungerToSave = 93
        elif(self.newHunger > 97 and self.newHunger <= 98):
            self.hungerToSave = 97
        elif(self.newHunger > 98 and self.newHunger <= 99):
            self.hungerToSave = 98
        else:
            self.hungerToSave = 99
    def normalize(self, rmin, rmax, value):
        tmin = 1
        tmax = 0

        value_normalized = ((value - rmin) / rmax - rmin) * (tmax - tmin) + tmin


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    socks = CommunicationSocket()
    start = Game()
    start.runGame()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
