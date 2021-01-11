# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 11:56:21 2020

@author: fuukv
"""

from mesa import Model
import math
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from LivAgent import LivAgent
from LivGovt import LocalGovt
from LivHazard import HazardAgent
from LivAid import AidWorker
import statistics as stats
import market as mrkt
import household as hsh
import shelter as shelter
import random 
import numpy as np
import pandas as pd
import hospital as hosp
from mesa.datacollection import DataCollector


def get_num_sick_agents(model):
    sick_agents = [a for a in model.schedule.agents if a.INF == 1]
    return len(sick_agents)

def get_num_immune_agents(model):
    immune_agents = [a for a in model.schedule.agents if a.REC == 1]
    return len(immune_agents)

def get_num_healthy_agents(model):
    healthy_agents = [a for a in model.schedule.agents if a.SUS == 1]
    return len(healthy_agents)

def get_num_exposed_agents(model):
    exp_agents = [a for a in model.schedule.agents if a.EXP == 1]
    return len(exp_agents)  

def get_num_agents_quarantine(model):
    sick_agents = [a for a in model.schedule.agents if a.quarantine == 1]
    return len(sick_agents)

def get_agents_unsheltered(model):
    unsheltered_agents = [a for a in model.schedule.agents if a.affected == 2]
    return len(unsheltered_agents)

def get_affected_agents(model):
    affected_agents = [a for a in model.schedule.agents if a.affected == 1]
    return len(affected_agents)

def get_average_liv_never_affected(model):
    avg_livelihood = [a.get_address().get_livelihood() for a in model.schedule.agents if type(a) == LivAgent and a.affected == 3]
    return np.mean(avg_livelihood)

def get_average_liv_affected(model):
    avg_livelihood = [a.get_address().get_livelihood() for a in model.schedule.agents if type(a) == LivAgent and a.affected != 3]
    return np.mean(avg_livelihood)

def get_shelter_infs(model):
    shelter_infections = [a for a in model.schedule.agents if a.cor_loc_shelter == True and type(a) == LivAgent]
    model.shelter_infections = len(shelter_infections)
    return len(shelter_infections)

def get_market_infs(model):
    market_infections = [a for a in model.schedule.agents if a.cor_loc_market == True and type(a) == LivAgent]
    model.market_infections = len(market_infections)
    return len(market_infections)

def get_hh_infs(model):
    household_infections = [a for a in model.schedule.agents if a.cor_loc_household == True and type(a) == LivAgent]
    model.household_infections = len(household_infections)
    return len(household_infections)

def get_average_livelihood(model):
    avg_livelihood = [(a.get_address().get_livelihood()/a.get_address().get_size()) for a in model.schedule.agents if type(a) == LivAgent]
    return np.mean(avg_livelihood)

def get_awareness(model):
    avg_awareness = np.average([agent.awareness for agent in model.schedule.agents if type(agent) == LivAgent])
    return avg_awareness

def get_lockdown_status(model):
    lockdown_status = model.g.lockdown_level
    return lockdown_status

def get_ppl_market(model):
    people_market = model.ppl_at_market
    return people_market

def get_nat_haz(model):
    if model.hazard:
        return 1
    else:
        return 0
    
def get_total_aid_delivered(model):
    delivered_aid = np.sum([aidworker.aid_delivered for aidworker in model.schedule.agents if type(aidworker) == AidWorker])
    return delivered_aid

def get_mld_days(model):
    if model.g.lockdown_level == 1:
        model.moderate_counter += 1
    return model.moderate_counter

def get_nld_days(model):
    if model.g.lockdown_level == 0:
        model.no_counter += 1
    return model.no_counter

def get_sld_days(model):
    if model.g.lockdown_level == 2:
        model.severe_counter += 1
    return model.severe_counter

def get_shelter_time(model):
    return model.shelter_time

def get_warning(model):
    return model.g.warning

def count_sheltered_agents(model):
    agent_sheltered = [agent for agent in model.schedule.agents if agent.in_shelter == 1]
    #agent_shelter = [agent.in_shelter for agent in model.schedule.agents]
    #sheltered = sum(1 for i in agent_shelter if i == 1)
    print(len(agent_sheltered))
    return len(agent_sheltered)

def get_shelter_pop(model):
    return model.shelter_pop

#kan korter    
def compute_low_livelihoods(model):
    livelihood_list = []
    low_livelihood_list = []
    low_liv_counter = 0
    for household in model.list_households:
        livelihood_hh = ([a.get_address().get_livelihood() for a in household.agents])
        livelihood_list.append(np.mean(livelihood_hh))
        if np.mean(livelihood_hh) < model.g.livelihood_threshold:
            low_livelihood_list.append(household)
    for hh in low_livelihood_list:
        low_liv_counter += 1
    #print(low_liv_counter, ": is the low liv counter")
    return low_liv_counter

def compute_ok_livelihoods(model):
    livelihood_list = []
    ok_livelihood_list = []
    ok_liv_counter = 0
    for household in model.list_households:
        #print("numer of agents in this hh: ", len(household.agents) )
        livelihood_hh = ([a.get_address().get_livelihood() for a in household.agents])
        livelihood_list.append(np.mean(livelihood_hh))
        if np.mean(livelihood_hh) > model.g.livelihood_threshold:
            ok_livelihood_list.append(household)
    for hh in ok_livelihood_list:
        ok_liv_counter += 1
    #print("ok liv counter is: ", ok_liv_counter)
    return ok_liv_counter

def get_max_contacts_shelter(model):
    return model.max_contacts_shelter
        

class LivModel_SIR(Model):
    def __init__(self, seed, width, height, initial_live, check, num_agents, corona_threshold,
                 growth_threshold, corona_fraction, E0, shelter_frac, A0, awareness_policy, awareness_effect,
                 livelihood_threshold, corona_switch, hazard_switch, livelihood_switch, num_aidworkers, testing_switch, test_frequency,
                 market_capacity, min_contacts, med_contacts, max_contacts, population_density, shelter_density, max_farm_liv_closed,
                 min_farm_liv_closed, max_cit_liv_closed, min_cit_liv_closed, max_farm_liv_open,
                 min_farm_liv_open, max_cit_liv_open, min_cit_liv_open, isolation_duration,
                 decrease_liv_aid, decrease_liv_mask, ptrans, precov, num_shelters, cash_transfer_policy,
                 corona_prioritization, height_cash, max_contacts_shelter, shelter_perc_meeting):
        self._seed = seed
        self.random.seed(seed)
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.check = check
        self.hazard = False
        self.num_agents = num_agents
        self.shelter_frac = shelter_frac
        self.max_cap = math.ceil(num_agents * self.shelter_frac) #maximum capacity of shelter
        self.E0 = E0
        self.A0 = A0
        self.my_market = mrkt.Market(10,20,num_agents*market_capacity)
        self.hazard_count = 0
        self.protection = 0 #in severe lockdown, protection changes to 1
        self.running = True # otherwise the model does not run
        self.ppl_at_market = 0
        self.initial_live = initial_live
        
        self.shelter_perc_meeting = shelter_perc_meeting
        self.min_contacts = min_contacts
        self.med_contacts = med_contacts
        self.max_contacts = max_contacts
        self.max_contacts_shelter = math.ceil(self.num_agents * self.shelter_frac * self.shelter_perc_meeting)
        
        self.market_infections = 0
        self.shelter_infections = 0
        self.household_infections = 0
        
        self.corona_switch = corona_switch
        self.hazard_switch = hazard_switch
        self.livelihood_switch = livelihood_switch
        self.testing_switch = testing_switch
        
        self.awareness_policy = awareness_policy
        self.awareness_effect = awareness_effect
        self.num_shelters = num_shelters
        self.cash_transfer_policy = cash_transfer_policy
        self.height_cash = height_cash
        self.corona_prioritization = corona_prioritization
        self.shelter_pop = []
        
        self.test_frequency = test_frequency
        self.decrease_liv_aid = decrease_liv_aid
        self.decrease_liv_mask = decrease_liv_mask
        self.waiting_time = 3 #wait this number of days before you get help with evacuation
        self.isolation_duration = isolation_duration
        
        self.no_counter = 0 #no days without lockdown
        self.count = 0 #counter for testing
        self.moderate_counter = 0 #no days moderate lockdown
        self.severe_counter = 0 #no. days severe lockdown
        self.shelter_time = 0 #time to spend in shelter
        
        #SIR parameters
        self.ptrans = ptrans #transmission chance is 10 percent
        self.precov = precov #recovery period is 1 days, so 1/14
        self.corona_fraction = corona_fraction #number of absolute cases corona 
        self.datacollector = DataCollector(
                model_reporters={
                        "Infected": get_num_sick_agents,
                        "Recovered": get_num_immune_agents,
                        "Susceptible": get_num_healthy_agents,
                        "Exposed": get_num_exposed_agents,
                        "Quarantine_aa": get_num_agents_quarantine,
                        "Avg_livelihood" : get_average_livelihood,
                        "livelihood_affected":get_average_liv_affected,
                        "livelihood_unaffected": get_average_liv_never_affected,
                        "lockdown_status" : get_lockdown_status,
                        "people_at_market": get_ppl_market,
                        "natural_hazard" : get_nat_haz,
                        "total_aid_delivered" : get_total_aid_delivered,
                        "total_sheltered_agents": count_sheltered_agents,
                        "affected_agents": get_affected_agents,
                        "total_unsheltered_agents":get_agents_unsheltered,
                        "no_lockdown": get_nld_days,
                        "moderate_lockdown": get_mld_days,
                        "severe_lockdown": get_sld_days,
                        "low_liv_counter": compute_low_livelihoods,
                        "ok_liv_counter": compute_ok_livelihoods,
                        "avg_awareness": get_awareness,
                        "Shelter_time": get_shelter_time,
                        "warning": get_warning,
                        "shelter_pop": get_shelter_pop,
                        "max_shelter_con": get_max_contacts_shelter,
                        "shelter_infs": get_shelter_infs,
                        "market_infs": get_market_infs,
                        "household_infs": get_hh_infs
           
                        },
                agent_reporters = {
                    "contacts": lambda x: x.exposure,
                    },
                )
        print(self.max_contacts_shelter)
        
        #Create agents
        #Create agents
        self.list_of_agents = []
        for i in range(self.num_agents):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            pos = (x,y)
            a = LivAgent(unique_id = i, pos = pos, model = self, 
                         market_pos = self.my_market.get_coordinates(), max_farm_liv_closed =  max_farm_liv_closed,
                         min_farm_liv_closed = min_farm_liv_closed, max_cit_liv_closed = max_cit_liv_closed, 
                         min_cit_liv_closed = min_cit_liv_closed, max_farm_liv_open = max_farm_liv_open, 
                         min_farm_liv_open = min_farm_liv_open, max_cit_liv_open = max_cit_liv_open, min_cit_liv_open = min_cit_liv_open,
                         isolation_duration = isolation_duration, decrease_liv_aid = decrease_liv_aid,
                         decrease_liv_mask = decrease_liv_mask)
            self.grid.place_agent(a, (x, y))
            a.set_occupation(np.random.choice(np.arange(1,3), p=[0.3,0.7])) #30% chance on being a farmer
            self.list_of_agents.append(a)
            self.schedule.add(a)
                    
        patient_zero = random.sample(self.list_of_agents, self.E0) #currently 1 citizen starts with infection
        for patient in patient_zero:
            patient.SUS = 0
            patient.EXP = 1
            patient.age = 40 #make sure agent goes to market
            
        ############################ AWARENESS #########################################
        if self.awareness_policy == True:
            target_agents = random.sample(self.list_of_agents, self.A0)
            for agent in target_agents:
                agent.awareness = 1
        
        #create households, assuming average 5 people per household
        nr_households = math.ceil((population_density * self.num_agents))
        
        #Initialize list with all households
        self.list_households = []
        for i in range(nr_households):
            new_household = hsh.Household(i)
            new_household.add_occupant(self.list_of_agents[i], initial_live) #Add first occupant to each household
            self.list_of_agents[i].set_address(new_household)
            self.list_households.append(new_household)

        #Assign remaining agents to random households
        for agent in range(nr_households, len(self.list_of_agents)):
            household_draw = random.randint(0, nr_households-1)
            for h in self.list_households:
                if h.get_id() == household_draw:
                    h.add_occupant(self.list_of_agents[agent], initial_live)
                    self.list_of_agents[agent].set_address(h)
        
        #reset addresses of agents to live with their household           
        for household in self.list_households:
            household.reset_address()
        
        #create shelters
        nr_shelters = self.num_shelters #math.ceil(self.num_agents * shelter_density)
        self.list_shelters = []
        for i in range(nr_shelters):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            pos = (x,y)
            max_cap = self.max_cap
            #print("Shelter is positioned at: ", pos)
            new_shelter = shelter.Shelter(i,pos, max_cap)
            self.list_shelters.append(new_shelter)
        
        #create the local government
        self.g = LocalGovt(-99,(1,1),self,lockdown_level = 0, corona_threshold = corona_threshold,
                           livelihood_threshold = livelihood_threshold, growth_threshold = growth_threshold,
                           list_of_agents = self.list_of_agents,
                           list_households = self.list_households)
        self.g.cases_threshold = self.num_agents * self.corona_fraction
        
        #initiate the location for the hazard so that it is visible in the visualization
        self.nat_haz = []
        for i in range(1):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.pos = (x,y)
            #base the probability on historical data of severity of natural hazards
            severity = np.random.choice(np.arange(1,6), p=[0.4,0.3,0.15,0.1,0.05])
            self.shelter_time = severity * 5 #minimum of 5, maximum of 25 days in shelter
            self.nh = HazardAgent(-3, self.pos, self, severity)
            self.grid.place_agent(self.nh, (x, y))
            self.nat_haz.append(self.nh)
        
        self.agent_data = []

        nr_hospitals = math.ceil(self.num_agents*0.00017)
        self.list_hospitals = []
        for i in range(nr_hospitals):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            pos = (x,y)
            new_hospital = hosp.Hospital(i, pos)
            self.list_hospitals.append(new_hospital)
                    
    #corona related        
    def get_market_exposure(self):
        cellmates = self.grid.get_cell_list_contents([self.my_market.get_coordinates()])
        if self.my_market.visitors == False and self.g.lockdown_level == 2 and len(cellmates)>max(self.min_contacts):
            for cellmate in cellmates:
                cellmate.contact_list = random.sample(cellmates, random.choice(self.min_contacts))
                cellmate.increase_awareness()
                cellmate.store_market_contacts()
        elif self.my_market.visitors == True and len(cellmates)>max(self.max_contacts): 
            for cellmate in cellmates:
                cellmate.contact_list = random.sample(cellmates, random.choice(self.max_contacts))
                cellmate.increase_awareness()
                cellmate.store_market_contacts()
        elif self.my_market.visitors == False and self.g.lockdown_level < 2 and len(cellmates)>max(self.med_contacts):
            for cellmate in cellmates:
                cellmate.contact_list = random.sample(cellmates, random.choice(self.med_contacts))
                cellmate.increase_awareness()
                cellmate.store_market_contacts()
        else: #not many people at market so you meet everyone there
            for cellmate in cellmates:
                for person in cellmates:
                    cellmate.contact_list += [person]
                cellmate.increase_awareness()
                cellmate.store_market_contacts()
    
    def night_exposure(self): #only for people sleeping in their homes or shelters
        for shelter in self.list_shelters:
            sheltermates = self.grid.get_cell_list_contents([shelter.pos])
            if len(sheltermates)>self.max_contacts_shelter:
                for sheltermate in sheltermates:
                    sheltermate.contact_list = random.sample(sheltermates, self.max_contacts_shelter)
                    sheltermate.increase_awareness()
                    sheltermate.store_sh_night_contacts()
            else:
                for sheltermate in sheltermates:
                    if isinstance(sheltermate, LivAgent):
                        for person in sheltermates:
                            if person not in sheltermate.contact_list and person.unique_id != sheltermate.unique_id:
                                sheltermate.contact_list += [person]
                        sheltermate.increase_awareness()
                        sheltermate.store_sh_night_contacts()
                
        for household in self.list_households:
            housemates = self.grid.get_cell_list_contents([household.pos])
            for individual in housemates:
                if isinstance(individual, LivAgent):
                    for housemate in housemates:
                        if housemate not in individual.contact_list and housemate.unique_id != individual.unique_id:
                            individual.contact_list += [housemate]
                    individual.store_hh_night_contacts()
                
                
    def recovery(self):
        for agent in self.list_of_agents:
            agent.recovery()
    
    def evening_program(self):
        for household in self.list_households:
            household.consume()   
     
    # testing plays a role in the model
    def testing(self):
        for agent in self.list_of_agents:
            if agent.INF == 1 and agent.symptoms == 1 and agent.REC != 1:
                agent.testing = 1                
                
    # testing is left out of scope in the model
    def no_testing(self):
        for agent in self.list_of_agents:
            agent.testing = 1 #people that are infected will immediately know
            
    def initiate_hazard(self):
        #if no hazard has happened yet
        if not self.hazard and self.hazard_switch == True and self.hazard_count != 4:
            #chance that natural hazard occurs
            if np.random.choice(np.arange(0,2), p=[0.50,0.50]) == 1:
                self.hazard = True
                affected_region = self.grid.get_neighbors(self.nh.pos,include_center = True, moore = True, radius = self.nh.radius)
                for agent in affected_region:
                    if type(agent)==LivAgent:
                        if agent.affected == 0:
                            agent.affected = 1
                if agent not in affected_region:
                    if type(agent)==LivAgent:
                        agent.affected = 3 #3 means never been affected
        
    def compute_livelihood_per_household(self):
        livelihood_list = []
        low_livelihood_list = []
        if self.livelihood_switch == True:
            for household in self.list_households:
                livelihood_hh = ([a.get_address().get_livelihood() for a in household.agents])
                livelihood_list.append(np.mean(livelihood_hh))
                if np.mean(livelihood_hh) < self.g.livelihood_threshold:
                    low_livelihood_list.append(household)
        else:
            for household in self.list_households:
                household.set_livelihood(self.initial_live)
                livelihood_hh = ([a.get_address().get_livelihood() for a in household.agents])
                livelihood_list.append(np.mean(livelihood_hh))
                if np.mean(livelihood_hh) < self.g.livelihood_threshold:
                    low_livelihood_list.append(household)
        
    def to_shelter(self):
        x = [shelter for shelter in self.list_shelters if shelter.full == True]
        if self.g.warning == True:
            nr_shelters = len(self.list_shelters)
            i = 0
            for agent in self.list_of_agents:
                if isinstance(agent, LivAgent):
                    while self.list_shelters[i].full == True and len(x) != len(self.list_shelters):
                        i = (i+1) % nr_shelters
                        x = [shelter for shelter in self.list_shelters if shelter.full == True]
                    if agent.affected == 1 and agent.in_shelter == 0 and (agent.need_help == 0 or agent.need_help == 1) and len(x) != len(self.list_shelters): #affected agents only & those who are not in shelter yet
                        agent.order_shelter(self.list_shelters[i])
                        i = (i+1) % nr_shelters
                    elif isinstance(agent, LivAgent) and agent.affected == 1 and len(x) == len(self.list_shelters):
                     agent.affected = 2
                     
                    else:
                        pass
                else:
                    pass

        elif self.g.warning == False: 
            #print("random shelter")
            for agent in self.list_of_agents:
                if isinstance(agent, LivAgent):              
                    if agent.affected == 1 and agent.in_shelter == 0 and (agent.need_help == 0 or agent.need_help == 1):
                        agent.random_shelter()
        else:
            pass
   
    def check_shelter_cap(self):
        x = [shelter for shelter in self.list_shelters if shelter.full == True]
        fs = np.asarray(x)
        print(fs.all(), "all true?")
        
    def get_agents_per_shelter(self):
        list_shelters = [len(shelter.agents) for shelter in self.list_shelters]
        self.shelter_pop = list_shelters
             
    def calculate_distance(self, pos1, pos2):
        return abs(pos1[0]-pos2[0]) + abs(pos1[1]-pos2[1])        
     
    def step(self):
        self.my_market.open = True
        self.ppl_at_market = 0 #reset number of people at market
        self.schedule.step_day() #during the day they go to the market
        if self.corona_switch == True:
            #print("corona is on bitches")
            self.get_market_exposure()
        else:
            pass
        if self.testing_switch == False:
            self.no_testing()
        else:
            if self.count < self.test_frequency:
                self.count += 1
            else:
                self.testing()
                self.count = 0
        self.schedule.step_night()
        self.evening_program() #eat livelihood
        self.compute_livelihood_per_household()
        if self.corona_switch == True:
            self.night_exposure()
            self.recovery()
        self.g.step() #government action at the end of the day
        self.initiate_hazard()
        
        if self.hazard == True:
            if self.g.warning == True and self.hazard_count < 4:
                self.hazard_count += 1
                if self.hazard_count == 3:
                    self.to_shelter()
                    self.hazard_count += 1 #so they don't shelter again
            elif self.g.warning == False and self.hazard_count != 4: #without warning
                self.to_shelter()
                self.hazard_count = 4 #so they don't shelter again
            else:
                pass
        else:
            pass
        self.get_agents_per_shelter()
        #use datacollector for model variables
        self.datacollector.collect(self)
        self.schedule.time += 1
        #stop running after 40 days
        if self.schedule.time >= 40:
            self.running = False
            #self.df.to_csv("results_13_okt.csv")
        
        
            
    def run_model(self):
        for i in range(40):
            self.step()
