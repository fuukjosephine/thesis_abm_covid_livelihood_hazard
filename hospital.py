# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 14:56:52 2020

@author: fuukv
"""

class Hospital():
    def __init__(self, unique_id, pos):
        self.id = unique_id
        self.x = pos[0] #x-coordinate of hospital
        self.y = pos[1] #y-coordinate of hospital
        self.cap = 50 #capacity of hospital #fixed --> to do 
        self.pos = (self.x,self.y)
        
    def get_coordinates(self):
        return (self.x, self.y)
    
    def get_capacity(self):
        return self.cap
    
    def is_open(self, no_agents):
        return no_agents <= self.cap #maybe useless
    
    def set_coordinates(self,x,y):
        self.x = x
        self.y = y
        
    def set_capacities(self,capacity):
        self.cap = capacity