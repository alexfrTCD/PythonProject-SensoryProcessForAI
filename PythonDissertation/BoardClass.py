# -*- coding: utf-8 -*-
"""
Created on Mon June  27 20:07:31 2022

@author: Alex
"""

import random

class Board():
    """
    class of the board to display
    """

    def __init__(self,rows,columns,possiblePositions):
        self.possiblePositions = possiblePositions
        print("possiblePosition: ", sorted(possiblePositions))
        self.rows = rows
        print("rows: ",rows)
        self.columns = columns
        print("columns: ",columns)
        #self.ambientTemperature = ambientTemperature


#init()
