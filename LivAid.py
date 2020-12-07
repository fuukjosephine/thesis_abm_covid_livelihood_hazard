# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 14:51:44 2020

@author: fuukv
"""

from mesa import Agent
import numpy as np
import random

class AidWorker(Agent):
    def __init__(self, unique_id, pos, model):
        super().__init__(unique_id, pos, model)
        #self.exposure = exposure
        self.INF = 0
        self.REC = 0
        self.SUS = 0
        self.EXP = 0
        self.quarantine = 0
        self.contacts = 0
        self.address = pos
        self.helped = 0
        self.aid_delivered = 0
        self.age = random.randint(18,80)
        self.occupation = 3 #occupation 3 = aid worker
        self.affected = 0
        self.in_shelter = 0 
        self.type = type(self)
        self.awareness = 0
    
    #get exposure of individual
    def get_exposure(self):
        return self.exposure
    
    def get_address(self):
        return self.address
        
    def set_address(self, address):
        self.address = address
        
    def increase_exposure(self, delta):
        self.exposure = (self.exposure + delta) * self.immune
        
    def provide_livelihood(self):   
        if self.helped == 0:        
            for household in self.model.list_households:
                liv = household.get_livelihood()
                if liv < 3 and household.aid == 0 and self.helped == 0:
                    household.increase_livelihood(1)
                    household.aid = 1
                    self.aid_delivered += 1
                    #print("Household ", household.id, " received aid from aid worker no. ", self.unique_id)
                    self.helped = 1
        #provide livelihood to household
    
    def get_supplies(self):
        self.helped = 0
        count = 0
        #when all households have received aid at least once, all households can receive aid again.
        for household in self.model.list_households:
            if household.aid == 1:
                count += 1
        if count == len(self.model.list_households):
            for household in self.model.list_households:
                household.aid = 0
        
    def evacuate(self):
        pass
    #if evacuation is necessary, help one of the families that needs help
    
    def retrieve_data(self):
        pass
    
    def step_night(self):
        pass
    
    def step_day(self):
        pass
    
    def step_aid(self):
        self.get_supplies()
        self.provide_livelihood()
        self.evacuate()
        