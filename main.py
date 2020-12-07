# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 12:30:26 2020

@author: fuukv
"""

import LivModel_SIR
import matplotlib.pyplot as plt 
import datetime
import time
import random
import numpy as np

#steering board
initial_live = round(random.uniform(1,10)) #initial livelihood
check = 0
num_aidworkers = 0
num_agents = 1000 + num_aidworkers #population size
E0 = 10 #initial number of exposed people
A0 = 0

#exposure_threshold = 6.5 
livelihood_threshold = 1
corona_switch = True
testing_switch = True #include or exclude testing from the model
test_frequency = 3 #test every 3 days
market_capacity = 0.8 #max cap is 80% of population
population_density = 0.15 #on average households of 7/8 people
shelter_density = 0.001 #shelters per population based on 6 shelters for 6000 people
seed1 = 45
np.random.seed(seed1)
corona_threshold = False #if false, corona is ok
corona_fraction = 0.1 #absolute cases of corona before lockdown is severed
growth_threshold = 10 #if more than 10 percent change of corona cases, lockdown is needed
ptrans = 0.1
precov = 1/14

awareness_policy = False
awareness_effect = 0.1
corona_prioritization = False
height_cash = 7
cash_transfer_policy = False

#contact rates at market
shelter_perc_meeting = 0.2 #you meet 20% of people staying at shelter?
min_contacts = [1,2,3]
med_contacts = [2,3,4]
max_contacts = [3,4,5]
max_contacts_shelter = [5,6,7,8,9,10]

max_farm_liv_open = 1.5
max_farm_liv_closed = 0.5
min_farm_liv_open = 1
min_farm_liv_closed = 0.5

max_cit_liv_open = 3
max_cit_liv_closed = 1
min_cit_liv_open = 2
min_cit_liv_closed = 1

livelihood_switch = True
hazard_switch = True
num_shelters = 9


decrease_liv_aid = -1.0
decrease_liv_mask = -0.5
shelter_time = random.randint(3,30) #number of days people have to evacuate before they are to return home
shelter_frac = 0.05

reset_time = 10 #after 10 days without corona, exposure is reset
isolation_duration = 14 #need 14 days in isolation when getting corona


#create the model with N agents        
model = LivModel_SIR.LivModel_SIR(width = 50, height = 50,seed = seed1, shelter_frac = shelter_frac,
                 initial_live = initial_live, check = check, num_agents = num_agents,
                 corona_threshold = corona_threshold, livelihood_threshold = livelihood_threshold,
                 corona_switch = corona_switch, livelihood_switch = livelihood_switch, hazard_switch = hazard_switch,
                 num_aidworkers = num_aidworkers, testing_switch = testing_switch, E0 = E0, A0 = A0,
                 growth_threshold = growth_threshold, corona_fraction = corona_fraction,
                 test_frequency = test_frequency, market_capacity = market_capacity,
                 awareness_policy = awareness_policy, awareness_effect = awareness_effect,
                 min_contacts = min_contacts, med_contacts = med_contacts, max_contacts = max_contacts,
                 population_density = population_density, ptrans = ptrans, precov = precov,
                 shelter_density = shelter_density, max_farm_liv_closed = max_farm_liv_closed, min_farm_liv_closed = min_farm_liv_closed,
                 max_cit_liv_closed = max_cit_liv_closed, min_cit_liv_closed = min_cit_liv_closed, 
                 max_farm_liv_open = max_farm_liv_open, min_farm_liv_open = min_farm_liv_open, 
                 max_cit_liv_open = max_cit_liv_open, min_cit_liv_open = min_cit_liv_open,
                 isolation_duration = isolation_duration, decrease_liv_aid = decrease_liv_aid, 
                 decrease_liv_mask = decrease_liv_mask, num_shelters = num_shelters,
                 cash_transfer_policy = cash_transfer_policy, corona_prioritization = corona_prioritization,
                 height_cash = height_cash, max_contacts_shelter = max_contacts_shelter, shelter_perc_meeting = shelter_perc_meeting )

exposure = []

begin_time = datetime.datetime.now()
#the model runs for three steps (e.g. three days)
for i in range(40):
    model.step()
    
model_df = model.datacollector.get_model_vars_dataframe()
# =============================================================================
# agent_df = model.datacollector.get_agent_vars_dataframe()
# agent_df = agent_df.reset_index()
# =============================================================================

#agentsssss = model.df.to_csv("agents_17sept.csv")

model_df.to_csv("df_12nov_5000.csv")
# =============================================================================
# agent_df.to_csv("agent_df.csv")
# =============================================================================

            
run_time = datetime.datetime.now() - begin_time
print("the run time was: ", run_time)

# =============================================================================
# print("size of agent df is: ", agent_df.size)
# =============================================================================
print("size of model df is: ", model_df.size)

model_df.plot()
model_df.Avg_livelihood.plot()
# =============================================================================
# agent_df.plot()
# =============================================================================
