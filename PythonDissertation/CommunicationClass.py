# -*- coding: utf-8 -*-
"""
Created on Mon June  27 20:03:46 2022

@author: Alex
"""


import socket
from dataclasses import dataclass

from ObjectClass import Object


# Socket comunication.
# import time


@dataclass
class IntrinsicVariable:
    distance: float
    value: float

class CommunicationSocket:

    def __init__(self):
        self.host, port = "127.0.0.1", 25003
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, port))
        self.totalList = []
    def receiveInfo(self, messageType):
        if(messageType=="number"):
            info = self.sock.recv(16).decode("UTF-8")
            try:
                info = int(info)
            except:
                info = float(info)
        elif(messageType == "char"):
            info = self.sock.recv(1).decode("UTF-8")

        #In this case, the info is a string

        elif(messageType == "name"):
            #name of an object is limited to 10
            firstInfo = self.sock.recv(16).decode("UTF-8")
            found = False
            info=""
            count = 0
            while(found == False):
                #print("info= ", info)
                if(firstInfo[count] == '-'):
                    #print("found true")
                    found = True
                else:
                    #print("found false")
                    info = info+firstInfo[count]
                    count = count +1

        else:
            # is is not an integer or a float,or a char, the info received is a string
            firstInfo = self.sock.recv(64).decode("UTF-8")
            found = False
            info=""
            count = 0
            while(found == False):
                if(firstInfo[count] == '-'):
                    found = True
                else:
                    info = info+firstInfo[count]
                    count = count +1


        return info

    def sendInfo(self, info, infoType):

        if(infoType=="Vector3"):
            maxBytes = 16
            for i in range(3):
                while(len(str(info[i])) < maxBytes):
                    info[i] = "0"+str(info[i])
            info = ','.join(map(str, info))  # Converting Vector3 to string
        elif(infoType=="action"):
            #print("action sended: ", info)
            maxBytes = 16
            while(len(info) < maxBytes):
                info= str(info) + "0"
            #print("final info: " , info)

        elif(infoType=="float"):
            maxBytes = 16
            while(len(str(info)) < maxBytes):
                info = "0" + str(info)
            #print("float sent: " , info)
        #The other option is that info is a bool, which is always 1 length size
        self.sock.send(info.encode("UTF-8"))


    def initAvatarPosition(self):
        positionX = self.receiveInfo("number")
        print("position x avatar= ", positionX)
        positionY = self.receiveInfo("number")
        positionZ = self.receiveInfo("number")
        print("init avatar position = ", positionX, positionZ)


        return (positionX,positionZ)

    def initAvatarRotation(self):
        rotationX = self.receiveInfo("number")
        rotationZ = self.receiveInfo("number")
        print("Init rotation" , rotationX,rotationZ)
        return (rotationX, rotationZ)


    def connectionMovement(self, action):
        self.sendInfo(action, "action")

    def initBoard(self):
        possiblePositions = []
        cols = self.receiveInfo("number")
        rows = self.receiveInfo("number")
        num = self.receiveInfo("number")
        #print("num possible positions", num)
        for x in range(int(num)):
            valueX = self.receiveInfo("number")
            valueZ = self.receiveInfo("number")
            #print("possible position= ", valueX, valueZ)
            possiblePositions.append((valueX, valueZ))

        #print("possible Positions: " , possiblePositions)
        return rows,cols,possiblePositions

    def actualizePossiblePositions(self):
        possiblePositions = []
        num = self.receiveInfo("number")
        #print("num possible positions", num)
        for x in range(int(num)):
            valueX = self.receiveInfo("number")
            valueZ = self.receiveInfo("number")
            #print("possible position= ", valueX, valueZ)
            possiblePositions.append((valueX, valueZ))

        #print("possible Positions: " , possiblePositions)
        return possiblePositions

    def receiveNewObjectPosition(self):

        positionX = self.receiveInfo("number")
        #print("positionX " , positionX)
        positionY = self.receiveInfo("number")
        #print("positionY " , positionY)
        positionZ = self.receiveInfo("number")
        #print("positionZ ", positionZ)
        return positionX,positionY,positionZ

    def receiveSensesInfo(self):
        temperatureFelt = self.receiveInfo("number")
        glareFelt = self.receiveInfo("number")
        soundFelt = self.receiveInfo("number")

        self.totalList = []
        touchList = []
        sightList = []
        #print("receiveSensesInfo")
        senseString = self.receiveSenseName()
        #print("Sight string = ", senseString)
        lengthSenseList = self.receiveInfo("number")
        #print("Length sight list: ", lengthSenseList)
        for i in range(lengthSenseList):
            sightList.append(self.receiveObject())
            #print(sightList[i].objectType)

        touchString = self.receiveSenseName()
        #print("touch string = ", senseString)
        lengthSenseList = self.receiveInfo("number")
        #print("Length touch list: ",  lengthSenseList)
        for i in range(lengthSenseList):
            touchList.append(self.receiveObject())
            #print(touchList[i].name)
        finalDict = {senseString:sightList, touchString :touchList}

        """
        print("senses info received")
        for key, value in finalDict.items():
            for i in range(len(value)):
                row,column = value[i].position
                print(key, 'row : ', row)
                print(key, 'column : ', column)
        """



        return int(temperatureFelt),int(glareFelt),int(soundFelt), sightList


    def receiveDrivesInfo(self):
        newHealth = self.receiveInfo("number")
        newHunger = self.receiveInfo("number")

        return newHealth, newHunger

    def receiveObject(self):
        name = self.receiveInfo("name")
        #print("object name= ", name)
        #print("character", character)
        positionX, positionY, positionZ = self.receiveNewObjectPosition()
        #print("position received= ", positionX,positionY,positionZ)
        distanceToAvatar = self.receiveInfo("number")
        #print("distace to avatar: ", distanceToAvatar)
        return Object(name, (positionX, positionZ), distanceToAvatar)

    def receiveSenseName(self):
        senseNumber = self.receiveInfo("number")
        #print("sense number", senseNumber)
        #print("Sense number received= ", senseNumber)
        if(senseNumber == 0): return "sight"
        elif(senseNumber == 1): return "smell"
        elif(senseNumber == 2): return "sound"
        elif(senseNumber == 3): return "taste"
        else: return "touch"
