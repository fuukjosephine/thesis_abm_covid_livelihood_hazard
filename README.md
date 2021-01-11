# thesis_abm_covid_livelihood_hazard

Model instructions

There are 13 .py files, of which 11 that are needed to run the simulation.

	File name	Content
1	Batch_SIR_22okt.py	To run experiments/batches
2	Server_SIR.py	File to launch the webserver
3	LivModel_SIR.py	The model file
4	LivAgent.py	The agent file
4	LivGovt.py	The government file
5	LivHazard.py	The hazard file
6	LivAid.py	The aidworkers file
7	Market.py	Contains market class
8	Shelter.py	Contains shelter class
9	Household.py	Contains household class
10	Hospital.py	Contains hospital class

In order to run the simulation, only the batch_SIR_22okt.py needs to be opened. With the current settings, around 850 runs are performed. Some errors might occur, that can be fixed in the following way:

Fixing "AttributeError: 'RandomActivation' object has no attribute 'step_day'"

1. Go to LivModel.py --> _init_() function --> line "self.schedule = RandomActivation(self)
2. Strg + Click on "RandomActivation" --> opens time.py
3. Add the following functions to RandomActivation class

		def step_day(self) -> None:
		        """ Executes the step of all agents, one at a time, in
		        random order.
		
		        """
		        for agent in self.agent_buffer(shuffled=True):
		            agent.step_day()
		# =============================================================================
		#         self.steps += 1
		#         self.time += 1
		# =============================================================================
		        
		    def step_night(self) -> None:
		        """ Executes the step of all agents, one at a time, in
		        random order.
		
		        """
		        for agent in self.agent_buffer(shuffled=True):
		            agent.step_night()
		# =============================================================================
		#         self.steps += 1
		#         self.time += 1
		# =============================================================================
		    def step_aid(self) -> None:
		        """ Executes the step of all agents, one at a time, in
		        random order.
		
		        """
		        for agent in self.agent_buffer(shuffled=True):
		            agent.step_aid()


Fixing "TypeError: __init__() missing 1 required positional argument: 'model' "
1. Go to LivAgent.py --> go to imports --> from mesa import Agent 
2. Strg + Click on "Agent" --> opens agent.py
3. Change the following function in Agent class

		From: 
		# =============================================================================
		#     def __init__(self, unique_id: int, model: Model) -> None:
		#         """ Create a new agent. """
		#         self.unique_id = unique_id
		#         self.model = model
		# =============================================================================

		To:         
		    def __init__(self, unique_id: int, pos:(int,int) , model: Model) -> None:
			""" Create a new agent. """
			self.unique_id = unique_id
			self.model = model
			self.pos = pos

Alternative: only add the pos:(int,int) to the __init__ and as attribute to the function.



