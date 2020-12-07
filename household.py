# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 15:29:57 2020

@author: fuukv
"""

import statistics as stats
import random
import numpy as np

class Household():
    def __init__(self, household_id):
        self.id = household_id # Id of household
        self.agents = [] #List of occupants
        self.size = len(self.agents)
        self.livelihood = 0
        self.pos = (0,0)
        self.aid = 0
        self.hazard_exposure = random.uniform(0,1)
        self.cash = 0 #turns to 1 if received cash transfer
        
        
    def add_occupant(self, agent, initial_live):
        self.agents.append(agent)
        self.livelihood += initial_live
        
    def add_occupants(self, agents, initial_live): 
        for i in agents:
            self.agents.append(i)
            self.livelihood += initial_live #later add random stuff
    
    def get_occupants(self):
        return self.agents
    
    def reset_address(self):
        for agent in self.agents:
            agent.home = self.agents[0].home
            agent.model.grid.move_agent(agent, agent.home)
            #print(agent.unique_id, " and I live: ", agent.home, "which is at household: ", agent.get_address())
            self.pos = agent.home
            self.home = agent.home
            #set hazard exposure to correpond with agent hazard exposure
            agent.hazard_exposure = self.hazard_exposure
            agent.need_help = np.random.choice(np.arange(0,2), p=[1-agent.hazard_exposure, agent.hazard_exposure])
            #print("agent hazard exposure is: ", agent.hazard_exposure, ' corresponds to hh NHexposure: ', self.hazard_exposure)
        #print("Household: ", self.id, " is positioned at ", self.pos)
        
    def get_id(self):
        return self.id
        
    def get_name(self):
        return "Household " + str(self.id)
    
    def get_size(self):
        return len(self.agents)
    
    def get_livelihood(self):
        return self.livelihood
    
    def set_livelihood(self, livelihood):
        self.livelihood = livelihood
        
    def increase_livelihood(self, livelihood):
        self.livelihood += livelihood
        #print("livelhood increased by ", livelihood, "to ", self.livelihood)
        
    def consume(self):
        self.livelihood = self.livelihood - self.get_size()
# =============================================================================
#         
#     def get_total_livelihood(self):
#         return sum([agent.get_livelihood() for agent in self.agents])
#     
#     def get_avg_livelihood(self):
#         return stats.mean([agent.get_livelihood() for agent in self.agents])
# =============================================================================
        