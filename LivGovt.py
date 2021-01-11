# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 16:25:54 2020

@author: fuukv
"""
from mesa import Agent
import numpy as np

class LocalGovt(Agent):
    def __init__(self, unique_id,pos, model, livelihood_threshold, growth_threshold, 
                 lockdown_level, corona_threshold, list_of_agents, list_households):
        super().__init__(unique_id, pos, model)
        self.list_of_agents = list_of_agents
        self.model = model
        self.livelihood_threshold = livelihood_threshold
        self.corona_threshold = corona_threshold
        self.cases_threshold = 0
        self.growth_threshold = growth_threshold
        self.list_households = list_households
        self.lockdown_level = [0, 1, 2] # 0=no lockdown, 1=medium lockdown, 2=severe lockdown
        self.warning = np.random.choice([True, False], p=[0.5,0.5]) #half the time there is an early warning
        self.avg_livelihood = self.calculate_livelihood()
        self.total_corona = 0 
        self.avg_contacts = 0
        self.cases = 0
        self.lockdown_time = 0
        
    #lockdown levels: 0=no lockdown, 1=moderate lockdown, 2=severe lockdown
    def impose_restrictions(self):
        if self.lockdown_time <= 0: 
            if self.avg_livelihood < self.livelihood_threshold and self.corona_threshold == False:
                self.lockdown_level = 0 #corona good, livelihood not, so all can go to market
            elif self.corona_threshold == True and self.avg_livelihood < self.livelihood_threshold:
                self.lockdown_level = 1 #corona not good, livelihood also not, but people need to go out
                self.lockdown_time = 14
            elif self.corona_threshold == True and self.avg_livelihood >= self.livelihood_threshold: #corona not good, livelihood good, so lockdown everything!
                self.lockdown_level = 2
                self.lockdown_time = 14
            elif self.corona_threshold == False and self.avg_livelihood >= self.livelihood_threshold: #corona good, livelihood is not
                self.lockdown_level = 0
            else:
                print("this should not be possible")
            
    def prioritize_corona(self):
        if self.lockdown_time <= 0:
            if self.avg_livelihood < self.livelihood_threshold and self.corona_threshold == False:
                self.lockdown_level = 0 #corona good, livelihood not, so all can go to market
            elif self.corona_threshold == True and self.avg_livelihood < self.livelihood_threshold:
                self.lockdown_level = 2 #corona not good, livelihood also not, but people need to go out
                self.lockdown_time = 14
            elif self.corona_threshold == True and self.avg_livelihood >= self.livelihood_threshold: #corona not good, livelihood good, so lockdown everything!
                self.lockdown_level = 2
                self.lockdown_time = 14
            elif self.corona_threshold == False and self.avg_livelihood >= self.livelihood_threshold: #corona good, livelihood is not
                self.lockdown_level = 0
            else:
                print("this should not be possible")
  
    def enforce_lockdown(self):
        if self.lockdown_level == 0:
            self.model.my_market.cap = self.model.my_market.max_cap
            self.model.my_market.visitors = True
            self.model_protection = 0
        elif self.lockdown_level == 1:
            self.model.my_market.cap = self.model.my_market.med_cap
            self.model.my_market.visitors = False
            self.model.protection = 0
        else:
            self.model.my_market.cap = self.model.my_market.min_cap
            self.model.my_market.visitors = False
            self.model.protection = 1
         
    def calculate_livelihood(self):
        avg_livelihood = 0
        for household in self.list_households:
            avg_livelihood += household.get_livelihood()
        avg_livelihood = avg_livelihood/len(self.list_households)
        return avg_livelihood
        
    def get_change(self, current, previous):
        if current == previous:
            return 0
        try:
            return (current - previous) / previous * 100.0
        except ZeroDivisionError:
            return 0
    
    def calculate_corona(self):
        corona_cases = 0
        for agent in self.model.list_of_agents:
            if agent.INF == 1:
                corona_cases += 1
        factor_increase = self.get_change(corona_cases, self.cases)
        #print("factor increase: ", factor_increase, "corona_cases: ", corona_cases)
        self.cases = corona_cases
        if factor_increase > self.growth_threshold and self.cases > self.cases_threshold:
            self.corona_threshold = True
        else:
            self.corona_threshold = False
        #print(factor_increase, ": R and absolute cases: ", corona_cases)
        return self.corona_threshold

    def set_corona(self):
        self.total_corona = self.calculate_corona      
    
    def calculate_contacts(self):
        for agent in self.model.list_of_agents:
            agent.calculate_exposure
        avg_contacts = [agent.exposure for agent in self.list_of_agents]
        self.avg_contacts = np.mean(avg_contacts)
        return self.avg_contacts
    
    def cash_transfer(self):
        for household in self.model.list_households:
            #if the livelihood is less than what is necessary for consumption
            if (household.livelihood / len(household.agents)) < 1 and household.cash != 1: 
                #give aid for one week
                household.livelihood += len(household.agents) * self.model.height_cash
                household.cash = 1
    
    def step(self):
        self.total_corona = self.calculate_corona()
        self.avg_livelihood = self.calculate_livelihood()
        
        #in case of different prioritization use below instead of impose_restrictions
        if self.model.corona_prioritization == True:
            self.prioritize_corona()
        else:
            self.impose_restrictions()
        self.enforce_lockdown()
        if self.model.cash_transfer_policy == True:
            self.cash_transfer()
        self.calculate_contacts()
        self.lockdown_time -= 1
        