# -*- coding: utf-8 -*-
"""
Created on Mon June  27 20:06:202 2022

@author: Alex
"""
import random

import numpy as np

import BoardClass
from qLearning import qLearning


class Avatar():
    """
    Class of the NPC that will learn from the external stimulus
    """
    def __init__(self, position, rotation):

        self.position = position
        self.rotation = rotation
        self.totalActions = ["rotRight" , "rotLeft" , "rotUp" , "rotDown","up", "down", "left", "right", "idle", "eat"]
        self.hunger = 0
        self.health = 100
        self.happiness = 50
        self.totalSteps = 0
        self.maxSteps = 100
    def chooseAction(self,foodPos, obs, qlearning, board):
        obs = tuple(obs)

        if foodPos not in list(qlearning.q_table.keys()):
            #print(qlearning.q_table)
            #print(type(obs))
            #print(obs)
            qlearning.q_table[foodPos] = {}
            qlearning.q_table[foodPos]["epsilon"] = qlearning.epsilon
            qlearning.q_table[foodPos]["notAchieved"] = 0
            qlearning.q_table[foodPos]["achieved"] = 0
        if obs not in list(qlearning.q_table[foodPos].keys()):
            qlearning.q_table[foodPos][obs]={}
            qlearning.q_table[foodPos][obs]["senses"] = {}
            qlearning.q_table[foodPos][obs]["actions"] = {}
            qlearning.q_table[foodPos][obs]["everything"] = {}
            qlearning.q_table[foodPos][obs]["senses"]["temperature"] = 1
            qlearning.q_table[foodPos][obs]["senses"]["glare"] = 1
            qlearning.q_table[foodPos][obs]["senses"]["soundIntensity"] = 1

            qlearning.q_table[foodPos][obs]["everything"]["temperature"] = 1
            qlearning.q_table[foodPos][obs]["everything"]["glare"] = 1
            qlearning.q_table[foodPos][obs]["everything"]["soundIntensity"] = 1

            qlearning.q_table[foodPos][obs]["everything"]["position"] = 0
            qlearning.q_table[foodPos][obs]["everything"]["rotation"] = 0

            qlearning.q_table[foodPos][obs]["everything"]["hunger"] = 0
            qlearning.q_table[foodPos][obs]["everything"]["health"] = 0

            for action in self.totalActions:
                if (self.check_movement(action, board)):
                    qlearning.q_table[foodPos][obs]["actions"][action] = 0
                    qlearning.q_table[foodPos][obs]["everything"][action] = 0
                    qlearning.q_table[foodPos][obs]["everything"][action+"_reward"] = 0

        if(self.totalSteps < self.maxSteps):
            #print("Steps made: " , self.totalSteps)
            if(foodPos == (-1,-1)):
                number = random.random()
                if number > 1: #>0.4
                    #print("Not random option")
                    action = max(qlearning.q_table[foodPos][obs]["actions"], key=qlearning.q_table[foodPos][obs]["actions"].get)
                    self.executeMovement(action)
                else:
                    #print("Random option")
                    action = self.random_movement(board, list(qlearning.q_table[foodPos][obs]["actions"].keys()))
                    self.executeMovement(action)

            else:
                self.totalSteps = self.totalSteps+1
                number = random.random()
                if number > qlearning.q_table[foodPos]["epsilon"]:
                    #print("Not random option")
                    action = max(qlearning.q_table[foodPos][obs]["actions"], key=qlearning.q_table[foodPos][obs]["actions"].get)
                    self.executeMovement(action)
                else:
                    #print("Random option")
                    action = self.random_movement(board, list(qlearning.q_table[foodPos][obs]["actions"].keys()))
                    self.executeMovement(action)
        else:
            action = "notAchieved"
        return action

    def random_movement(self,board, possibleActions):

        possibleFound = False
        actionsNotChecked = possibleActions.copy()
        #print("possible actions: " , actionsNotChecked)
        while(possibleFound == False):
            #print("Length actions", len(actionsNotChecked) - 1)
            randomChoice = random.randint(0,len(actionsNotChecked) - 1)
            #print("actions not checked: ", actionsNotChecked)
            #print("actions not checked length: ", len(actionsNotChecked))
            #print("randomChoice: ", randomChoice)
            if self.check_movement(actionsNotChecked[randomChoice],board) == True:
                #print("posible actions at the decision: ", actionsNotChecked)
                #print("action choosed: " , actionsNotChecked[randomChoice])
                possibleFound = True
            else:
                #print("Action discarded: ", actionsNotChecked[randomChoice])
                actionsNotChecked.pop(randomChoice)
        action = actionsNotChecked[randomChoice]

        return action
    def executeMovement(self, movement):
        #print("execute movement")
        if movement == "down":
            self.position = (self.position[0] + 0, self.position[1] -1 )

        elif movement == "moveDownRot":
                self.position = (self.position[0] + 0, self.position[1] -1 )
                self.rotation = (0,-1)
        elif movement == "left":
            self.position = (self.position[0] -1, self.position[1] + 0)

        elif movement == "moveLeftRot":
                self.position = (self.position[0] -1, self.position[1] + 0)
                self.rotation = (-1,0)
        elif movement == "right":
            self.position = (self.position[0] + 1, self.position[1] + 0)

        elif movement == "moveRightRot":
            self.position = (self.position[0] + 1, self.position[1] + 0)
            self.rotation = (1,0)

        elif movement == "up":
            self.position = (self.position[0] +0, self.position[1] + 1)

        elif movement == "moveUpRot":
            self.position = (self.position[0] +0, self.position[1] + 1)
            self.rotation = (0,1)

        #Rotation case
        elif movement == "rotRight":
            self.rotation = (1, 0)
        elif movement == "rotLeft":
            self.rotation = (-1, 0)
        elif movement == "rotUp":
            self.rotation = (0, 1)
        elif movement == "rotDown":
            self.rotation = (0, -1)

    def check_pos(self, sightList, avatar):
        pos = (-1,-1)
        #print("Action choosed = " , movement)
        foodList = []
        counter = 0
        notFound = True
        while counter < len(sightList) and notFound:
            #print("Object type: ", sightList[counter].objectType)
            if sightList[counter].objectType == "Food":
                pos = sightList[counter].position
                notFound = False
            else:
                counter = counter + 1

        return pos


    def check_eat_basic(self, foodPos):
        XAux = self.position[0] + self.rotation[0]
        ZAux = self.position[1] + self.rotation[1]

        if (XAux, ZAux) == foodPos:
            return True

    def check_eat(self, board, sightList):

        #If the avatar is looking to some object, I can try to eat
        XAux = self.position[0] + self.rotation[0]
        ZAux = self.position[1] + self.rotation[1]

        #print("Action choosed = " , movement)
        eatFood = False
        eatPossible = True
        counter = 0
        while counter < len(sightList) and eatFood == False:
            #print("Object type: ", sightList[counter].objectType)
            if sightList[counter].position == (XAux, ZAux):
                print("Eat object type = ", sightList[counter].objectType , " at position : ", sightList[counter].position )
                if sightList[counter].objectType == "Food":
                    #print("EatFood = True")
                    eatFood = True
                else:
                    counter = counter + 1
            return (eatPossible, eatFood)

    def check_movement(self, movement, board):
        """
        Checks is the movement proposed is possible or not taking into account the position and the direction.
        """
        if movement == "idle":
            return True
        #print("Position inside check_mov: ", self.position)
        X,Z = self.position

        if movement == "down" or movement == "moveDownRot":
            Z-=1
        elif movement == "left" or movement == "moveLeftRot":
            X-=1
        elif movement == "right" or movement == "moveRightRot":
            X+=1
        elif movement == "up" or movement == "moveUpRot":
            Z+=1
        elif movement == "eat":
            #If the avatar is looking to some object, I can try to eat
            XAux = self.position[0] + self.rotation[0]
            ZAux = self.position[1] + self.rotation[1]
            #print("Board possible positions: ", board.possiblePositions)
            #print("Board rwos and cols: ", board.rows, board.columns)
            if (XAux, ZAux) in board.possiblePositions:
                #print("can't eat because there is nothing")
                return False
            if XAux > board.columns-1 or ZAux > board.rows-1:
                #print("eat discarded because it's too out")
                return False
            if ZAux<0 or XAux<0:
                #print("eat discarded because it's negative")
                #print("num columns: ", board.columns)
                #print("num rows: ", board.rows)

                return False
            else:
                #print("Action choosed = " , movement)
                return True

        #Rotation case
        elif movement == "rotRight" or "rotLeft" or "rotUp" or "rotDown":
            return True
        else:
            return False

        if (X,Z) not in board.possiblePositions:
            #print("return false")
            return False

        return True

