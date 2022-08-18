# -*- coding: utf-8 -*-
"""
Created on Mon JuLY 12 11:27:19 2022

@author: Alex
"""
import ast
import collections
import csv
import math
import pickle
import random
import pandas as pd
import numpy as np

SHOW_EVERY = 0
class qLearning:

    def __init__(self):
        self.epsilon = 0.2
        #For no drives: 0.9995
        #Using drives: 0.99995
        self.max_exploration_rate = 0.2
        self.min_exploration_rate = 0.01
        self.exploration_decay_rate = 0.01
        self.actionsExecuted = 0
        self.numObsBefore = 0
        self.minimumExpRate = 0.01

        self.start_q_table = None #We can put a filename here to load an old q_table
        self.learning_rate = 0.75 #how quickly the agent abandons the previous Q-value. The higher the learning rate, the more quickly the agent will adopt the new Q-value.
        # if the learning rate is 1, the estimate for the Q-value for a given state-action pair would be the straight up newly calculated Q-value and would not consider previous Q-values that had been calculated for the given state-action pair at previous time steps
        self.discount = 0.75 #The biggest, the more important are the future rewards
        self.q_table = {}

    def actualizeTable(self, foodPos, obsBefore, obs, action, reward, temperature, glare, sound):
        self.actionsExecuted +=1
        #print("FoodPos in actualize Table" , foodPos)
        #print(self.q_table)
        #print("Obs before: ", obsBefore)
        #print("New obs: ", obs)
        if(obs[0] != obsBefore[0]):

            try:
                new_q = (1 - self.learning_rate) * self.q_table[foodPos][obsBefore]["actions"][action] + self.learning_rate*(reward + self.discount * self.q_table[foodPos][obs]["actions"][max(self.q_table[foodPos][obs]["actions"], key=self.q_table[foodPos][obs]["actions"].get)])
            except:
                new_q = reward

        else:
            new_q = reward

        #print("Obs in actualize table:", obs)
        #print("Action", action)
        #print("Old_q: ", old_q)
        #print("New q: " , new_q)

        #print("New q actualized for obs ", obs, "and action ", action)
        self.q_table[foodPos][obsBefore]["actions"][action] = new_q
        #print("new q: " , new_q ,"at obs: ", obsBefore)
        self.q_table[foodPos][obsBefore]["senses"]["temperature"] = temperature
        self.q_table[foodPos][obsBefore]["senses"]["glare"] = glare
        self.q_table[foodPos][obsBefore]["senses"]["soundIntensity"] = sound

        #The position of the state (before exeuting the action)
        self.q_table[foodPos][obsBefore]["everything"]["position"] = obsBefore[0]
        #The rotation of the state (before exeuting the action)
        self.q_table[foodPos][obsBefore]["everything"]["rotation"] = obsBefore[1]
        #The health of the state (before exeuting the action)
        #self.q_table[foodPos][obsBefore]["everything"]["health"] = obsBefore[2]
        #The hunger of the state (before exeuting the action)
        #self.q_table[foodPos][obsBefore]["everything"]["hunger"] = obsBefore[3]


        self.q_table[foodPos][obsBefore]["everything"][action] = new_q
        self.q_table[foodPos][obsBefore]["everything"][action+"_reward"] = reward
        self.q_table[foodPos][obsBefore]["everything"]["temperature"] = temperature
        self.q_table[foodPos][obsBefore]["everything"]["glare"] = glare
        self.q_table[foodPos][obsBefore]["everything"]["soundIntensity"] = sound

        """
            if(self.actionsExecuted == 10000):
            print("num obs before: ", self.numObsBefore)
            self.epsilon = self.epsilon * (len(self.q_table.keys()) - self.numObsBefore / 10000 - 0.1)
            self.numObsBefore = len(self.q_table.keys())
            self.actionsExecuted = 0
        """

        #print("Epsilon: ", self.epsilon)


    def printReward(self):
        print({'ep': [], 'avg': [], 'min': [], 'max': []})

    def initQtable(self):
        """
        if self.start_q_table != None:
            with open(self.start_q_table, "rb") as f:
                self.q_table = pickle.load(f)
        """
        if self.start_q_table is not None:
            totalObs = pd.read_csv(self.start_q_table, usecols = ['obs'])
            actions = pd.read_csv(self.start_q_table, usecols = ["up", "left", "right", "down", "moveRightRot", "moveLeftRot", "moveDownRot","moveUpRot", "rotRight", "rotLeft", "rotDown", "idle", "eat"])
            senses = pd.read_csv(self.start_q_table, usecols = ["temperature", "glare", "soundIntensity"])
            totalTemperatures = senses['temperature'].tolist()
            totalGlares = senses['glare'].tolist()
            totalSoundIntensities = senses['soundIntensity'].tolist()
            #print("TotalObs", totalObs)
            #print("First obs: ", ast.literal_eval(totalObs.values[0]))
            for i in range(len(totalObs)):
                self.q_table[totalObs[i].item()] = {}
                self.q_table[totalObs[i]]["actions"] = {}
                self.q_table[totalObs[i]]["senses"] = {}
                self.q_table[totalObs[i]]["everything"] = {}

                self.q_table[totalObs[i]]["senses"]["temperature"] = totalTemperatures[i]
                self.q_table[totalObs[i]]["senses"]["glare"] = totalGlares[i]
                self.q_table[totalObs[i]]["senses"]["soundIntensity"] = totalSoundIntensities[i]

                self.q_table[totalObs[i]]["everything"]["temperature"] = totalTemperatures[i]
                self.q_table[totalObs[i]]["everything"]["glare"] = totalGlares[i]
                self.q_table[totalObs[i]]["everything"]["soundIntensity"] = totalSoundIntensities[i]

            print("Init Q table: ", self.q_table)


