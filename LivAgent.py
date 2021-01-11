# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 11:09:05 2020

@author: fuukv
"""

from mesa import Agent
import random
import numpy as np

class LivAgent(Agent):
    def __init__(self, unique_id, pos, model, market_pos, max_farm_liv_closed,
                 min_farm_liv_closed, max_cit_liv_closed, min_cit_liv_closed, max_farm_liv_open,
                 min_farm_liv_open, max_cit_liv_open, min_cit_liv_open, isolation_duration,
                 decrease_liv_aid, decrease_liv_mask):
        super().__init__(unique_id, pos, model)
        #self.pos = pos
        
        self.SUS = 1
        self.EXP = 0
        self.INF = 0
        self.REC = 0  
        
        self.Ihh = 0 #infected encoutered at home
        self.Shh = 0 #susceptible encoutered at home
        self.Rhh = 0 #recovered encoutered at home
        self.Ehh = 0 #exposed encountered at home
        
        self.Ish = 0 #infected encoutered at shelter
        self.Ssh = 0 #susceptible encoutered at shelter
        self.Rsh = 0 #recovered encoutered at shelter
        self.Esh = 0 #exposed encountered at shelter
        
        self.Im = 0 #infected encoutered at market
        self.Sm = 0 #susceptible encoutered at market
        self.Rm = 0 #recovered encoutered at market
        self.Em = 0 #exposed encoutered at market
        
        self.cor_loc_market = False
        self.cor_loc_shelter = False
        self.cor_loc_household = False
        
        self.corona = 0 
        self.exposure = 1 #exposure measured in people met during 1 day
        self.incub_time = 5
        
        self.awareness = 0 #np.random.choice(np.arange(0,2), p=[0.5,0.5]) #random.uniform(0,1) #random number between 0 and 1
        self.symptoms = 1 #np.random.choice(np.arange(0,2), p=[0.18,0.82]) #18 percent chance no symptoms
        
        #initiate agents with age distribution: 5% older than 65 (working age)
        self.age = np.random.choice([40,80], p=[0.95,0.05])
        self.market_pos = market_pos
        self.home = pos
        self.occupation = np.random.choice([0,1], p=[0.35,0.65]) #1 is farmer, 0 is not
        self.quarantine_time = 0 #counts the days that you still need to be in quarantine
        self.quarantine = 0
        self.isolation_duration = isolation_duration #the days necessary in isolation after getting virus
        self.shelter_time = 0 #number of days in shelter, after 5 days they return home
        
        self.facemask = 0
        self.model = model
        
        self.affected = 0 #by natural hazard
        self.in_shelter = 0 #can only be added once to shelter
        self.hazard_exposure = 0
        self.hh_livelihood = 0
        self.testing = 0
        
        self.need_help = 0 #the chance that you need help during evacuation depends on your hazard exposure and some luck
        self.assistance_counter = 0
        
        #livelihood settings
        self.max_farm_liv_closed = max_farm_liv_closed
        self.min_farm_liv_closed = min_farm_liv_closed
        self.max_cit_liv_closed = max_cit_liv_closed
        self.min_cit_liv_closed = min_cit_liv_closed
        self.max_farm_liv_open = max_farm_liv_open
        self.min_farm_liv_open = min_farm_liv_open
        self.max_cit_liv_open = max_cit_liv_open
        self.min_cit_liv_open = max_cit_liv_open
        self.decrease_liv_aid = decrease_liv_aid
        self.decrease_liv_mask = decrease_liv_mask
        
        #contacts (social distancing)
        self.contact_list = [] #contact list of agents that they have encountered during one day
        self.contacts = 0
        self.contacts_market = 0
        self.contacts_night = 0
        self.type = type(self)
 
    def get_address(self):
        return self.address
        
    def set_address(self, address):
        self.address = address     

    def go_to_market(self):
        if self.model.g.lockdown_level == 2:
            if self.facemask == 0 and self.model.my_market.open == True and self.get_address().get_livelihood() < (self.get_address().get_size() * 2):
                self.buy_facemask()
                if self.age < 65 and self.quarantine_time == 0 \
                    and self.facemask == 1 and self.in_shelter == 0:
                    self.model.grid.move_agent(self, self.market_pos)
                    self.trade()
                    self.model.ppl_at_market +=1
            elif self.facemask == 1 and self.model.my_market.open == True and self.get_address().get_livelihood() < (self.get_address().get_size() * 2):
                if self.age < 65 and self.quarantine_time == 0 \
                    and self.facemask == 1 and self.in_shelter == 0:
                    self.model.grid.move_agent(self, self.market_pos)
                    self.trade()
                    self.model.ppl_at_market +=1
        
        elif self.model.g.lockdown_level != 2 and self.get_address().get_livelihood() < (self.get_address().get_size() * 2) \
            and self.age < 65 and self.quarantine_time == 0 and self.model.my_market.open == True and self.testing == 0 and self.in_shelter == 0:
                self.model.grid.move_agent(self, self.market_pos)
                self.trade()
                self.model.ppl_at_market +=1
        else:
            pass
            
    def go_home(self):
        #they can return home if (1) they're not in quarantine and not in the danger zone OR
        #(2) they are not in quarantine and they have already spent 5 days in the shelter
        if (self.quarantine_time == 0 and (self.affected == 0 or self.affected == 3) and self.quarantine == 0) or \
            (self.quarantine_time == 0 and self.shelter_time == self.model.shelter_time and self.quarantine == 0):
            self.model.grid.move_agent(self, self.home)
      
    def reset_contacts(self):
        self.contact_list = []
        self.contacts = 0
    
    def get_name(self):
        return "Agent " + str(self.unique_id)
    
    def get_contacts(self):
        return self.contacts
    
    def trade(self):
        #visitors are not allowed, not that much extra livelihood
        if self.model.my_market.visitors == False:
            if self.occupation == 1 and self.get_address().get_livelihood() < self.model.g.livelihood_threshold:
                self.get_address().increase_livelihood(self.max_farm_liv_closed)
            elif self.occupation == 1:
                self.get_address().increase_livelihood(self.min_farm_liv_closed)
            elif self.occupation != 1 and self.get_address().get_livelihood() < self.model.g.livelihood_threshold:
                self.get_address().increase_livelihood(self.max_cit_liv_closed)
            else:
                self.get_address().increase_livelihood(self.min_cit_liv_closed)
        #visitors are allowed, so more livelihood        
        else:
            if self.occupation == 1 and self.get_address().get_livelihood() < self.model.g.livelihood_threshold:
                self.get_address().increase_livelihood(self.max_farm_liv_open)
            elif self.occupation == 1:
                self.get_address().increase_livelihood(self.min_farm_liv_open)
            elif self.occupation != 1 and self.get_address().get_livelihood() < self.model.g.livelihood_threshold:
                self.get_address().increase_livelihood(self.max_cit_liv_open)
            else:
                self.get_address().increase_livelihood(self.min_cit_liv_open)
        
    def set_occupation(self, occupation):
        self.occupation = occupation
        
    def get_occupation(self):
        return self.occupation
                
    def check_market_capacity(self):
        cellmates = self.model.grid.get_cell_list_contents([self.market_pos])
        if len(cellmates) >= self.model.my_market.cap:
            self.model.my_market.open = False
        else:
            "still open for now"
    
    def to_quarantine(self):
        if self.testing == 1 and self.INF == 1 and self.quarantine == 1:
            self.quarantine_time = self.isolation_duration
            self.quarantine = 1
            ########ROOMMATES NEED TO QUARANTINE##############
            roomies = self.get_address().get_occupants()
            for roomie in roomies:
                roomie.quarantine = np.random.choice(np.arange(0,2), p=[1-roomie.awareness, roomie.awareness])
                if roomie.quarantine == 1:
                    roomie.quarantine_time = 14
        else:
            pass
    
    def order_shelter(self, shelter):
        if shelter.full == False:
            self.model.grid.move_agent(self, shelter.pos)
            shelter.add_occupant(self)
            self.affected = 1
            self.in_shelter = 1
    
    def random_shelter(self):
        my_shelter = self.model.list_shelters[0]
        my_dist = 10000 #np.inf        
        for shelter in self.model.list_shelters:           
            if shelter.full == False:              
                if self.model.calculate_distance(self.pos,shelter.pos) < my_dist:                   
                    my_dist = self.model.calculate_distance(self.pos,shelter.pos)
                    my_shelter = shelter            
        if my_dist != 10000:     
            self.model.grid.move_agent(self, my_shelter.pos)
            my_shelter.add_occupant(self)
            self.in_shelter = 1
        else:
            self.in_shelter = 0
            self.affected = 2
        
    
    #to do = wait for help (livelihood goes down, then still evacuate but set need_help to 0)    
    def wait_for_aid(self):
        if self.need_help == 1 and self.assistance_counter < self.model.waiting_time:
            self.assistance_counter += 1
            self.get_address().increase_livelihood(self.decrease_liv_aid)
        else:
            self.need_help = 0
            self.random_shelter()
    
    def get_position(self):
        return self.pos
    
    def increase_awareness(self):
        for agent in self.contact_list:
            self.awareness += agent.awareness * self.model.awareness_effect
            if self.awareness > 1:
                self.awareness = 1
    
    def store_market_contacts(self):
        #for person in self.contact_list:
        Sm = len([cellmate for cellmate in self.contact_list if cellmate.SUS == 1])
        Im = len([cellmate for cellmate in self.contact_list if cellmate.INF == 1])
        Rm = len([cellmate for cellmate in self.contact_list if cellmate.REC == 1])
        Em = len([cellmate for cellmate in self.contact_list if cellmate.EXP == 1])
        self.set_Sm(Sm)
        self.set_Im(Im)
        self.set_Rm(Rm)
        self.set_Em(Em)
        self.contacts_market = len(self.contact_list)
        self.contacts += len(self.contact_list)
        self.contact_list = []
     
    def set_Sm(self, Sm):
        self.Sm = Sm
    
    def set_Im(self, Im):
        self.Im = Im
        
    def set_Rm(self, Rm):
        self.Rm = Rm
    
    def set_Em(self, Em):
        self.Em = Em
        
    def store_hh_night_contacts(self):
        Shh = len([cellmate for cellmate in self.contact_list if cellmate.SUS == 1])
        Ihh = len([cellmate for cellmate in self.contact_list if cellmate.INF == 1])
        Rhh = len([cellmate for cellmate in self.contact_list if cellmate.REC == 1])
        Ehh = len([cellmate for cellmate in self.contact_list if cellmate.EXP == 1])
        self.set_Shh(Shh)
        self.set_Ihh(Ihh)
        self.set_Rhh(Rhh)
        self.set_Ehh(Ehh)
        self.contacts_night = len(self.contact_list)
        self.contacts += len(self.contact_list)
        self.contact_list = []
        if self.SUS == 1:
            self.get_corona()
            
    def set_Shh(self, Sh):
        self.Shh = Sh
        
    def set_Ihh(self, Ih):
        self.Ihh = Ih
        
    def set_Rhh(self, Rh):
        self.Rhh = Rh
        
    def set_Ehh(self, Eh):
        self.Ehh = Eh
            
    def store_sh_night_contacts(self):
        Ssh = len([cellmate for cellmate in self.contact_list if cellmate.SUS == 1])
        Ish = len([cellmate for cellmate in self.contact_list if cellmate.INF == 1])
        Rsh = len([cellmate for cellmate in self.contact_list if cellmate.REC == 1])
        Esh = len([cellmate for cellmate in self.contact_list if cellmate.EXP == 1])
        self.set_Ssh(Ssh)
        self.set_Ish(Ish)
        self.set_Rsh(Rsh)
        self.set_Esh(Esh)
        self.contacts_night = len(self.contact_list)
        self.contacts += len(self.contact_list)
        self.contact_list = []
        if self.SUS == 1:
            self.get_corona()         
        
    def set_Ssh(self, Sh):
        self.Ssh = Sh
        
    def set_Ish(self, Ih):
        self.Ish = Ih
        
    def set_Rsh(self, Rh):
        self.Rsh = Rh
        
    def set_Esh(self, Eh):
        self.Esh = Eh
        
    def get_corona(self):
        Nm = self.Im + self.Sm + self.Rm + self.Em
        Nhh = self.Ihh + self.Shh + self.Rhh + self.Ehh
        Nsh = self.Ish + self.Ssh + self.Rsh + self.Esh
        if Nm > 0 and self.corona != 1:
            dSdt_market = (self.contacts_market * self.model.ptrans * (self.Im + self.Em) * self.Sm) / Nm
            prob_market = dSdt_market / Nm
            if prob_market > 1:
                prob_market = 1
            self.corona = np.random.choice(np.arange(0,2), p=[1-prob_market, prob_market])
            if self.corona == 1:
                self.cor_loc_market = True
        elif Nm == 0:
            pass
        if Nhh > 0 and self.corona != 1:
            dSdt_night = (self.contacts_night * self.model.ptrans * (self.Ihh + self.Ehh) * self.Shh) / Nhh
            prob_night= dSdt_night / Nhh
            if prob_night > 1:
                prob_night = 1
            self.corona = np.random.choice(np.arange(0,2), p=[1-prob_night, prob_night]) 
            if self.corona == 1:
                self.cor_loc_household = True
        if Nsh > 0 and self.corona != 1:
            dSdt_night = (self.contacts_night * self.model.ptrans * (self.Ish + self.Esh) * self.Ssh) / Nsh
            prob_night= dSdt_night / Nsh
            if prob_night > 1:
                prob_night = 1
            self.corona = np.random.choice(np.arange(0,2), p=[1-prob_night, prob_night]) 
            if self.corona == 1:
                self.cor_loc_shelter = True       
        if self.corona == 1:
            self.INF = 0
            self.EXP = 1
            self.SUS = 0

    def recovery(self):
        if self.EXP == 1:
            self.incub_time -= 1
            self.REC = np.random.choice(np.arange(0,2), p = [1-self.model.precov, self.model.precov])
            if self.incub_time == 0:
                self.EXP = 0
                self.INF = 1
            if self.REC == 1 and self.incub_time == 0:
                self.INF = 0
                self.EXP = 0
                self.quarantine = 0
                self.testing = 0
        elif self.INF == 1:
            self.REC = np.random.choice(np.arange(0,2), p = [1-self.model.precov, self.model.precov])
            if self.REC == 1 and self.incub_time == 0:
                self.INF = 0
                self.EXP = 0
                self.quarantine = 0
                self.testing = 0
        else:
            pass
        
    def get_better(self):
        #get better after quarantine
        if self.INF == 1 and self.quarantine_time == 0:
            self.REC = 1
            self.INF = 0
            self.EXP = 0   
            self.quarantine = 0
            
    def change_exposed_status(self):
        if self.EXP == 1 and self.incub_time == 0:
            self.EXP = 0
            self.INF = 1
    
    def calculate_exposure(self):
        self.exposure = len(self.contacts)
        
    def buy_facemask(self):
        if self.model.protection == 1 and self.facemask == 0 and self.get_address().get_livelihood() > 0:
            self.get_address().increase_livelihood(self.decrease_liv_mask)
            self.facemask = 1
    
    def retrieve_data(self):
        return [self.model.schedule.time, self.type, self.age, self.affected, self.need_help]
    
    def step_day(self):
        self.reset_contacts()
        self.check_market_capacity()
        self.go_to_market()
    
    def step_night(self):
        self.go_home()
        #corona bit
        if self.model.corona_switch == True:
            if self.quarantine == 0 and self.testing == 1 and self.INF == 1: #if not quarantining, check if you need to quarantine
                self.quarantine = np.random.choice(np.arange(0,2), p=[1-self.awareness, self.awareness])
                if self.quarantine == 1:
                    self.to_quarantine()
                else:
                    self.awareness = 0
            if self.quarantine_time > 0:
                self.quarantine_time -= 1
                if self.quarantine_time == 0 and self.INF == 1:
                    self.get_better()          
        if self.in_shelter == 1:
            self.shelter_time += 1
            self.get_address().increase_livelihood(1) #get food from help organizations during shelter stay
            if self.shelter_time == self.model.shelter_time:
                self.shelter_time =+ 1
                self.in_shelter = 0
                self.affected = 0
                self.go_home()        
        self.change_exposed_status()        
        
    def step_aid(self):
        pass
            
        

        
        