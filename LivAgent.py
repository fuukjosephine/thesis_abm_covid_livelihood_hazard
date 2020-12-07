# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 11:09:05 2020

@author: fuukv
"""

from mesa import Agent
import random
import numpy as np
import math

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
        
        self.Ih = 0 #infected encoutered at home/shelter
        self.Sh = 0 #susceptible encoutered at home/shelter
        self.Rh = 0 #recovered encoutered at home/shelter
        self.Eh = 0 #exposed encountered at home/shelter
        self.Im = 0 #infected encoutered at market
        self.Sm = 0 #susceptible encoutered at market
        self.Rm = 0 #recovered encoutered at market
        self.Em = 0 #exposed encoutered at market
        
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
        #exposure goes up based on number of people at market, times their exposure
        #go to market if not too old & if livelihood is not covered for at least 3 days
        #cannot go to market if in shelter
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
            #print("my loc still market right??: ", self.pos, "xoxo", self.unique_id)
            self.model.grid.move_agent(self, self.home)
            #print("and now home: ", self.pos, "xoxo", self.unique_id)
      
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
                self.get_address().increase_livelihood(self.max_farm_liv_closed) #farmers get 5 livelihood if below threshold
                #print("livelihood went up by agent: ", self.unique_id)
            elif self.occupation == 1:
                self.get_address().increase_livelihood(self.min_farm_liv_closed) #otherwise just 3
                #print("livelihood went up by agent: ", self.unique_id)
            elif self.occupation != 1 and self.get_address().get_livelihood() < self.model.g.livelihood_threshold:
                self.get_address().increase_livelihood(self.max_cit_liv_closed) #get 3 livelhood if below threshold
                #print("livelihood went up by agent: ", self.unique_id)
            else:
                self.get_address().increase_livelihood(self.min_cit_liv_closed) #otherwise just 1
                #print("livelihood went up by agent: ", self.unique_id)
        #visitors are allowed, so more livelihood        
        else:
            if self.occupation == 1 and self.get_address().get_livelihood() < self.model.g.livelihood_threshold:
                self.get_address().increase_livelihood(self.max_farm_liv_open) #farmers get 10 livelihood if below threshold
                #print("livelihood went up by agent: ", self.unique_id)
            elif self.occupation == 1:
                self.get_address().increase_livelihood(self.min_farm_liv_open) #otherwise just 6
                #print("livelihood went up by agent: ", self.unique_id)
            elif self.occupation != 1 and self.get_address().get_livelihood() < self.model.g.livelihood_threshold:
                self.get_address().increase_livelihood(self.max_cit_liv_open) #get 6 livelhood if below threshold
                #print("livelihood went up by agent: ", self.unique_id)
            else:
                self.get_address().increase_livelihood(self.min_cit_liv_open) #otherwise just 2
                #print("livelihood went up by agent: ", self.unique_id)
        
    def set_occupation(self, occupation):
        self.occupation = occupation
        
    def get_occupation(self):
        return self.occupation
                
    def check_market_capacity(self):
        cellmates = self.model.grid.get_cell_list_contents([self.market_pos])
        if len(cellmates) >= self.model.my_market.cap:
            self.model.my_market.open = False
            #print("market is closed now")
        else:
            "still open for now"
    
    def to_quarantine(self):
        #print(self.testing, self.INF, self.quarantine)
        if self.testing == 1 and self.INF == 1 and self.quarantine == 1:
            #print("joe")
# =============================================================================
#             my_hospital = self.model.list_hospitals[0]
#             my_dist = 1000000
#             for hospital in self.model.list_hospitals:
#                 new_dist = self.model.calculate_distance(self.pos, hospital.pos)
#                 if new_dist < my_dist and hospital.cap != 0:
#                     my_dist = new_dist
#                     my_hospital = hospital
#             self.model.grid.move_agent(self, my_hospital.pos)
# =============================================================================
            self.quarantine_time = self.isolation_duration
            self.quarantine = 1
            
            
            ########ROOMMATES NEED TO QUARANTINE##############
            #print("uhhh")
            roomies = self.get_address().get_occupants()
            
            
            for roomie in roomies:
                roomie.quarantine = np.random.choice(np.arange(0,2), p=[1-roomie.awareness, roomie.awareness])
                if roomie.quarantine == 1:
                    roomie.quarantine_time = 14
                    #print("whatuup")
# =============================================================================
#             for roomie in roomies:
#                 #stay at home --> testing = 1
#                 roomie.testing = 1
#                 roomie.quarantine = 1
# =============================================================================
            #self.get_address().increase_livelihood(1)
        else:
            pass
    
    def order_shelter(self, shelter):
        if shelter.full == False:
            self.model.grid.move_agent(self, shelter.pos)
            shelter.add_occupant(self)
            self.affected = 1
            #print("about to enter shelter")
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
            #print("entered shelter, ", self.unique_id)
        else:
            #print("I cannot enter shelter", self.unique_id)
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
        #print(self.Sm, self.Im, self.Rm, self.Em)
     
    def set_Sm(self, Sm):
        self.Sm = Sm
    
    def set_Im(self, Im):
        self.Im = Im
        
    def set_Rm(self, Rm):
        self.Rm = Rm
    
    def set_Em(self, Em):
        self.Em = Em
        
    def store_night_contacts(self):
        Sh = len([cellmate for cellmate in self.contact_list if cellmate.SUS == 1])
        Ih = len([cellmate for cellmate in self.contact_list if cellmate.INF == 1])
        Rh = len([cellmate for cellmate in self.contact_list if cellmate.REC == 1])
        Eh = len([cellmate for cellmate in self.contact_list if cellmate.EXP == 1])
        self.set_Sh(Sh)
        self.set_Ih(Ih)
        self.set_Rh(Rh)
        self.set_Eh(Eh)
        self.contacts_night = len(self.contact_list)
        self.contacts += len(self.contact_list)
        self.contact_list = []
        if self.SUS == 1:
            self.get_corona()
            
        
    def set_Sh(self, Sh):
        self.Sh = Sh
        
    def set_Ih(self, Ih):
        self.Ih = Ih
        
    def set_Rh(self, Rh):
        self.Rh = Rh
        
    def set_Eh(self, Eh):
        self.Eh = Eh
        
    def get_corona(self):
        Nm = self.Im + self.Sm + self.Rm + self.Em
        Nh = self.Ih + self.Sh + self.Rh + self.Eh
        
        #print("infected close? " , self.Im, self.Ih)
        if Nm > 0 and self.corona != 1:
            dSdt_market = (self.contacts_market * self.model.ptrans * (self.Im + self.Em) * self.Sm) / Nm
            prob_market = dSdt_market / Nm
            if prob_market > 1:
                prob_market = 1
            #print(self.contacts_market)
            #print("contacts:", self.contacts_market, "ptrans", self.model.ptrans, "Im", self.Im, "Sm", self.Sm, "Em", self.Em, "Nm", Nm, "probab:", prob_market)
            self.corona = np.random.choice(np.arange(0,2), p=[1-prob_market, prob_market])
            #print("probmarket: ", prob_market, "corona? ", self.corona, "age?", self.age,
                  #" number of contacts: ", self.contacts)
            #print("my market prob was: ", prob_market) 
        elif Nm == 0:
            pass
            #print('wtf')
        if Nh > 0 and self.corona != 1:
            dSdt_night = (self.contacts_night * self.model.ptrans * (self.Ih + self.Eh) * self.Sh) / Nh
            prob_night= dSdt_night / Nh
# =============================================================================
#             if self.contacts_night > 50: 
#                 print("pos", self.pos, "contacts", self.contacts_night, "prob", prob_night, "ih", self.Ih)
#             print(self.contacts_night)
# =============================================================================
            if prob_night > 1:
                prob_night = 1
            #print("contacts:", self.contacts_night, "ptrans", self.model.ptrans, "Ih", self.Ih, "Sh", self.Sh, "Nm", Nh, "probab:", prob_night)
            self.corona = np.random.choice(np.arange(0,2), p=[1-prob_night, prob_night])
            
            
            #print("whereas my night prob was: ", prob_night)
            
           # print("probnight was: ", prob_night, " corona?: ", self.corona,
                  #"number of housemates: ", self.contacts)
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
        #always chance to recover, even without knowing you were sick in the first place
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
            #print(self.get_address().get_livelihood())
            self.get_address().increase_livelihood(self.decrease_liv_mask)
            self.facemask = 1
            #print("I, ", self.unique_id, ' have bought a facemask, now livelihood is: ', self.get_address().get_livelihood())
    
    def retrieve_data(self):
        return [self.model.schedule.time, self.type, self.age, self.affected, self.need_help]
    
    def step_day(self):
        self.reset_contacts()
        self.check_market_capacity()
        self.go_to_market()
    
    def step_night(self):
        self.go_home()
        #quarantine_time 0 means out of quarantine, or never been there
        #corona bit
        if self.model.corona_switch == True:
            if self.quarantine == 0 and self.testing == 1 and self.INF == 1: #if not quarantining, check if you need to quarantine
                self.quarantine = np.random.choice(np.arange(0,2), p=[1-self.awareness, self.awareness])
                if self.quarantine == 1:
                    self.to_quarantine()
                else:
                    #if you are not quarantining, you won't do it at all.
                    self.awareness = 0
            if self.quarantine_time > 0:
                self.quarantine_time -= 1
                if self.quarantine_time == 0 and self.INF == 1:
                    #after the quarantine time, even if still sick, will go out again?
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
            
        

        
        