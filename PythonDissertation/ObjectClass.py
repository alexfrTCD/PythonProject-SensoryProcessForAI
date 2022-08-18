# -*- coding: utf-8 -*-
"""
Created on Mon June  27 20:01:27 2022

@author: Alex
"""
from dataclasses import dataclass


@dataclass
class IntrinsicVariable:
    distance: float
    value: float

class Object:
    def __init__(self,objectType, position, distance):
        self.objectType = objectType
        self.position = position
        self.distance = distance

    def __str__(self):
        return f"{self.position}, {self.distance}"

    #Not for now
    def action(self):
        pass
