# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 13:20:54 2020

@author: fuukv
"""

import statistics as stats

class Shelter():
    def __init__(self, shelter_id, pos, max_cap):
        self.shelter_id = shelter_id # Id of shelter
        self.agents = [] #List of occupants
        self.pos = pos
        self.max_cap = max_cap #to do
        self.min_cap = self.max_cap * 0.5
        self.full = False

    def add_occupant(self, agent):
        #print("joe")
        self.agents.append(agent)
        #print(len(self.agents))
        self.check_capacity()
       
    def add_occupants(self, agents): 
        for i in agents:
            self.agents.append(i)
            self.check_capacity()
            
    def check_capacity(self):
        #print("agents in this shelter: ", len(self.agents), self.shelter_id)
        if len(self.agents) == self.max_cap:
            #print("agents in this shelter: ", len(self.agents), "shelter_id:", self.shelter_id)
            self.full = True
    
    
       
