
"""
Created on Fri Jul 24 13:15:06 2020

@author: fuukv
"""

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import (
    CanvasGrid,
    ChartModule,
    BarChartModule,
    PieChartModule,
    TextElement
)
from mesa.visualization.UserParam import UserSettableParameter
from LivModel_SIR import *
import math
import random

#steering board
initial_live = round(random.uniform(1,10)) #initial livelihood
check = 0
num_aidworkers = 0
num_agents = 1000 + num_aidworkers #population size
E0 = 1 #initial number of exposed people
A0 = 5

#exposure_threshold = 6.5 
livelihood_threshold = 5
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

#contact rates at market
shelter_perc_meeting = 0.2 #you meet 20% of people staying at shelter?
min_contacts = [1,2,3]
med_contacts = [2,3,4]
max_contacts = [3,4,5]
max_contacts_shelter = [5,6,7,8,9,10]
shelter_perc_meeting = 0.2

max_farm_liv_open = 1.5
max_farm_liv_closed = 0.5
min_farm_liv_open = 1
min_farm_liv_closed = 0.5

max_cit_liv_open = 3
max_cit_liv_closed = 1
min_cit_liv_open = 2
min_cit_liv_closed = 1


decrease_liv_aid = -1.0
decrease_liv_mask = -0.5
shelter_time = random.randint(3,30) #number of days people have to evacuate before they are to return home
shelter_frac = 0.05

reset_time = 10 #after 10 days without corona, exposure is reset
isolation_duration = 14 #need 14 days in isolation when getting corona

reset_time = 10
isolation_duration = 14 #need 14 days in isolation when getting corona

SICK_COLOR = "yellow"
# Red
IMMUNE_COLOR = "#FF3C33"
# Blue
HEALTHY_COLOR = "#3349FF"

#
EXPOSURE = "#46FF33"
LIVELIHOOD = "#FF3C33"

OLD_COLOR = "pink"
ADULT_COLOR = "green"
HAZARD_COLOR = "blue"
AFFECTED_COLOR = "orange"

#Lockdown
LOCKDOWN_COLOR = "lightgreen"

def agent_portrayal(agent):
    #seed1 = 44
    if agent is None:
        return
    
    portrayal = {}

    # update portrayal characteristics for each Person object
    if isinstance(agent, LivAgent):
        portrayal["Shape"] = "figures/house.png"
        portrayal["scale"] = 1.5
        portrayal["Layer"] = 0

        if agent.age > 65:
            color = OLD_COLOR
        else:
            color = ADULT_COLOR
            
        if agent.affected == 1: #agents that are affected by natural hazard
            portrayal["Shape"] = "figures/broken_house.png"
            
        if agent.INF == 1:
            portrayal["Shape"] = "figures/hospital.png"

        portrayal["Color"] = color
    
    if isinstance(agent, HazardAgent):
        portrayal["Shape"] = "figures/tornado.png"
        portrayal['scale'] = 1.5
        portrayal["Layer"] = 1  

    return portrayal

# dictionary of user settable parameters - these map to the model __init__ parameters
model_params = {
    "num_agents": UserSettableParameter(
        "number", "People", value = 100, description="Initial Number of People"),
    
    "E0": UserSettableParameter(
        "number", "Initial number of infected people", value = 20, description = "initial number of exposed"),
    
    "livelihood_threshold": UserSettableParameter(
        "slider",
        "livelihood threshold",
        5,0,20,1,
        description = "Livelihood threshold government"
        ),
    
    "corona_switch": UserSettableParameter(
        "checkbox", "epidemic",value = True
        ),
    
    "ptrans": UserSettableParameter(
        "slider", "transmission rate",
        0.1, 0.01, 0.2, 0.01,
        description = "transmission rate"
        ),
    
    "precov": UserSettableParameter(
        "slider", "recovery rate",
        0.07, 0.16, 0.4, 0.3,
        description = "recovery rate"
        ),        
    
    "growth_threshold": UserSettableParameter(
        "slider", "R in full percentages", 
        10, 1, 25, 1,
        description = "R in percentage points"
        ),
    
    "corona_fraction": UserSettableParameter(
        "slider", "ratio cases of COVID : population",
        0.1, 0.01, 0.2, 0.01,
        description = "COVID versus population"
        ),
    
    "hazard_switch": UserSettableParameter(
        "checkbox", "hazard", value = True
        ),
    
    "num_shelters": UserSettableParameter(
        "slider", "number of shelters",
        10, 1, 20, 1,
        description = "number of shelters"
        ),
    
    "shelter_frac": UserSettableParameter(
        "slider", "shelter capacity as percentage of population",
        0.05, 0.01, 0.1, 0.01,
        description = "shelter cap as percentage of population"
        ),
    
    "livelihood_switch": UserSettableParameter(
        "checkbox", "livelihood", value = True
        ),
    
    "testing_switch": UserSettableParameter(
        "checkbox", "testing", value = True
        ),
    
    "test_frequency": UserSettableParameter(
        "slider", 
        "test frequency",
        3,1,10,1, 
        description = "number of days between testing population"
        ),
    
    "awareness_policy": UserSettableParameter(
        "checkbox", "awareness campaign", value = False
        ),
    
    "awareness_effect": UserSettableParameter(
        "slider", "effect awareness per encounter",
        0.01, 0.0, 0.02, 0.005,
        description = "per encounter increased awareness"
        ),
    
    "corona_prioritization": UserSettableParameter(
        "checkbox", "corona prioritized over livelihood?",
        value = False,
        description = "corona prioritized over livelihood?"
        ),

    
# =============================================================================
#     "min_contacts": UserSettableParameter(
#         "number" ,"minimum no. of contacts", 
#         value = 5, description = "min contacts at market etc"
#         ),
#     
#     
#     "med_contacts": UserSettableParameter(
#         "number" ,"medium no. of contacts", 
#         value = 25, description = "med contacts at market etc"        
#         ),
#     
#     "max_contacts": UserSettableParameter(
#         "number" ,"maximum no. of contacts", 
#         value = 50, description = "max contacts at market etc"
#         ),
# =============================================================================
    
    "cash_transfer_policy": UserSettableParameter(
        "checkbox","cash transfer",
        value = False,
        description = "cash transfer policy"
        ),
    
     "height_cash": UserSettableParameter(
     "slider", "height of cash transfer",
     7, 0, 21, 7,
     description = "heigth of cash transfer in days extra (per week)"
     )
     ,
        
    "seed": seed1,  
    "width":45, 
    "height":45,
    "initial_live": initial_live, 
    "corona_threshold": corona_threshold,
    "check":check,
    "market_capacity": market_capacity,
    "num_aidworkers": num_aidworkers,
    "population_density": population_density,
    "shelter_density": shelter_density,
    "max_farm_liv_closed": max_farm_liv_closed,
    "min_farm_liv_closed": min_farm_liv_closed,
    "max_cit_liv_closed": max_cit_liv_closed,
    "min_cit_liv_closed": min_cit_liv_closed,
    "max_farm_liv_open": max_farm_liv_open,
    "min_farm_liv_open": min_farm_liv_open,
    "max_cit_liv_open": max_cit_liv_open,
    "min_cit_liv_open": min_cit_liv_open,
    "isolation_duration": isolation_duration,
    "decrease_liv_aid": decrease_liv_aid,
    "decrease_liv_mask": decrease_liv_mask,
    "A0": A0,
    "max_contacts_shelter": max_contacts_shelter,
    "min_contacts": min_contacts,
    "med_contacts": med_contacts,
    "max_contacts": max_contacts,
    "shelter_perc_meeting": shelter_perc_meeting
    }

grid = CanvasGrid(agent_portrayal, 50, 50, 500, 500)

# map data to chart in the ChartModule
chart_element_pop = ChartModule(
    [
        {"Label": "Infected", "Color": SICK_COLOR},
        {"Label": "Recovered", "Color": IMMUNE_COLOR},
        {"Label": "Susceptible", "Color": HEALTHY_COLOR},
        {"Label": "Exposed", "Color": AFFECTED_COLOR}
    ]
)

#hmmm hoe doe ik dit
shelter_bar = BarChartModule(
    [
        {"Label": "no_lockdown", "Color": "lightgreen"},
        {"Label": "moderate_lockdown", "Color": "green"},
        {"Label": "severe_lockdown", "Color": "lightblue"},
    ]
)

chart_element_awareness = ChartModule(
    [
     {"Label": "avg_awareness", "Color": LOCKDOWN_COLOR}
     ]
    )

chart_element_kpis = ChartModule(
    [
        {"Label": "Avg_livelihood", "Color": LIVELIHOOD}
    ]
)

#chart that shows with 0 - 1 - 2 what the lockdown status is
chart_element_lockdown = ChartModule(
    [
     {"Label": "lockdown_status", "Color": LOCKDOWN_COLOR},
     ]
    )

chart_element_nh = ChartModule(
    [
     {"Label": "natural_hazard", "Color": "pink"}
     ]
    )

chart_quarantine = ChartModule(
    [
     {"Label": "Quarantine_aa", "Color": "pink"}
     ]
    )


# =============================================================================
# agent_bar = BarChartModule(
#     [{"Label": "Wealth", "Color": MID_COLOR}],
#     scope="agent",
#     sorting="ascending",
#     sort_by="Wealth",
# )
# =============================================================================

agent_contacts = BarChartModule(
    [{"Label": "contacts", "Color": EXPOSURE}],
    scope="agent"
)

chart_marketppl = ChartModule(
    [
     {"Label": "people_at_market", "Color": OLD_COLOR}
     ])


agent_liv_bar = BarChartModule(
    [
     {"Label": "HH_livelihood", "Color": LIVELIHOOD
      }
     ])

household_liv_bar = BarChartModule(
    [
     {"Label": "low_liv_counter", "Color": "yellow"},
     {"Label": "ok_liv_counter", "Color": "green"}
     ])

sheltered_agents = ChartModule(
    [
     {"Label": "total_sheltered_agents", "Color": "black"},
     {"Label": "total_unsheltered_agents", "Color": "red"},
     {"Label": "affected_agents", "Color": "green"}
     ]
    )

lockdown_days = PieChartModule(
    [
     {"Label": "no_lockdown", "Color": "lightgreen"},
      {"Label": "moderate_lockdown", "Color": "green"},
      {"Label": "severe_lockdown", "Color": "lightblue"}
     ]
    )

lockdown_bar = BarChartModule(
    [
        {"Label": "no_lockdown", "Color": "lightgreen"},
        {"Label": "moderate_lockdown", "Color": "green"},
        {"Label": "severe_lockdown", "Color": "lightblue"},
    ]
)

server = ModularServer(
    LivModel_SIR,
    [grid, chart_element_pop,
     chart_element_awareness,
     chart_element_kpis, 
     chart_quarantine,
     chart_element_nh,
     #agent_contacts,
     chart_element_lockdown,
     household_liv_bar,
     sheltered_agents,
     chart_marketppl,
     lockdown_days,
     lockdown_bar],
    "Liv Model SIR",
    model_params = model_params
    )

server.port = 8532 # The default
server.launch()