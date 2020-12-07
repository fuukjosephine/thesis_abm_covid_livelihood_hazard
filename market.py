# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 15:21:41 2020

@author: fuukv
"""

class Market():
    def __init__(self, x, y, capacity):
        self.x = x #x-coordinate of market
        self.y = y #y-coordinate of market
        self.cap = capacity #capacity of market
        self.open = True
        self.visitors = True
        self.max_cap = capacity
        self.med_cap = capacity * 0.5
        self.min_cap = capacity * 0.2
        self.pos = (self.x, self.y)
        
    def get_coordinates(self):
        return (self.x, self.y)
    
    def get_capacity(self):
        return self.cap
    
    def is_open(self, no_agents):
        return no_agents <= self.cap
    
    def set_coordinates(self,x,y):
        self.x = x
        self.y = y
        
    def set_capacities(self,capacity):
        self.cap = capacity
    
    
        