# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 11:31:41 2020

@author: fuukv
"""

from mesa import Agent

class HazardAgent(Agent):
    def __init__(self, unique_id, pos, model, severity):
        super().__init__(unique_id, pos, model)
        self.severity = severity
        #randomness
        self.radius = severity * 8 #experiment with this one #to do
        self.contacts = 0
        self.quarantine = 0
        self.SUS = 0
        self.INF = 0
        self.EXP = 0
        self.REC = 0
        self.contact_list = 0
        self.awareness = 0
        

    def get_severity(self):
        return self.severity
   
    def get_radius(self, radius):
        self.radius = radius
     
    def get_position(self):
        return self.pos
    
    def set_position(self, pos):
        self.pos = pos

            
        

        
        