import random
import env
import KnowledgeBase
import AstarSearch

NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

class LogicAgent(object):
	"""
	A hybrid agent that uses logic and a planner to work its way through the
	wumpus world
	"""

	def __init__(self):
		"""
		Initializes the agent
		"""
		self.logic = None
		self.environ = None
		self.timer = 0
		self.hasArrow = True
		self.KB = None

	def search(self, environment, logicEngine): #TODO TODO TODO
		"""
		Runs the program loop.
		"""
		self.environ = environment
		self.logic = logicEngine
		self.hasArrow = True
		success = False
		dead = False
		haveGold = False
		x, y = (1,1)
		facing = NORTH

		# persistent agent variables
		self.KB = KnowledgeBase.KnowledgeBase(self.logic)
		self.KB.initWumpusWorldLogic()
		self.timer = 0 # timer
		self.plan = [] # action sequence

		# "hack" to include these percepts for environment
		scream = False
		bump = False

		while not success and not dead:
			# get percepts
			(breeze, stench, glitter) = self.environ.sense(x,y)

			dead = self.environ.isDeadly(x,y)

			if not dead:
				action = self.hybridWumpusAgent([glitter, stench, breeze, bump, scream], (x, y), facing)

				if bump:
					bump = False
				if scream:
					scream = False

				if action == "Forward":
					if facing == NORTH:
						bump = self.environ.canMove(x, y+1)
						if not bump:
							(x, y) = (x, y+1)
					if facing == EAST:
						bump = self.environ.canMove(x+1, y)
						if not bump:
							(x, y) = (x+1, y)
					if facing == SOUTH:
						bump = self.environ.canMove(x, y-1)
						if not bump:
							(x, y) = (x, y-1)
					if facing == WEST:
						bump = self.environ.canMove(x-1, y)
						if not bump:
							(x, y) = (x-1, y)
				elif action == "TurnLeft":
					facing = facing - 1 % 4
				elif action == "TurnRight":
					facing = facing + 1 % 4
				elif action == "Shoot" and self.hasArrow:
					wumpusHit = self.environ.shootArrow(x, y, facing)
					self.hasArrow = False
					if wumpusHit:
						scream = True
				elif action == "Grab":
					if glitter and not haveGold:
						haveGold = True
				elif action == "Climb":
					if (x, y) == (0, 0):
						success = True
					#else:
					#	break

		return (success, dead, self.timer, self.hasArrow)

	### Wumpus Hybrid Algorithm ###

	def hybridWumpusAgent(self, percept, current, facing):
		"""
		Main logic algorithm.
		percept is a list of True/False: [glitter, stench, breeze, bump, scream]
		"""
		# tell agent the percepts and therefore breezy, smelly
		self.KB.tellPercepts(percept, self.timer, current)

		# tell agent the current square is visited and safe
		self.KB.tell("Visited(Pos("+str(current[0])+","+str(current[1])+"))")
		self.KB.tell("Safe(Pos("+str(current[0])+","+str(current[1])+"))")

		# get all squares that are safe
		safe = [(x,y) for x in range(0, self.environ.size) for y in range(0, self.environ.size) if self.KB.ask("Safe(Pos("+str(x)+","+str(y)+"))")]

		unvisited = []
		if self.KB.ask("GlitterAt("+str(self.timer)+")"):
			self.plan = ["Grab"] + self.planRoute(current, facing, [(0,0)], safe) + ["Climb"]

		if self.plan == []:
			unvisited = [(x,y) for x in range(0, self.environ.size) for y in range(0, self.environ.size) if self.KB.ask("-Visited(Pos("+str(x)+","+str(y)+"))")]
			self.plan = self.planRoute(current, facing, list(set(unvisited).intersection(set(safe))), safe)

		if self.plan == [] and self.ask("HaveArrow("+str(self.timer)+")"):
			possibleWumpus = [(x,y) for x in range(0, self.environ.size) for y in range(0, self.environ.size) if not self.KB.ask("-Wumpus(Pos("+str(x)+","+str(y)+"))")]
			self.plan = self.planRoute(current, facing, possibleWumpus, safe)

		if self.plan == []: # no choice, but to take a risk
			notUnsafe = [(x,y) for x in range(0, self.environ.size) for y in range(0, self.environ.size) if not self.KB.ask("-OK(Pos("+str(x)+","+str(y)+",),"+str(t)+")")]
			self.plan = self.planRoute(current, facing, list(set(unvisited).intersection(set(notUnsafe))), safe)

		if self.plan == []:
			self.plan = self.planRoute(current, facing, [(0,0)], safe) + ["Climb"]

		action = self.plan.pop(0)

		self.KB.tell(self.KB.makeActionStatement(action, self.timer))
		self.timer += 1

		return action

	def planRoute(self, current, facing, goals, allowed):
		"""
		Plan a route. Calls A*.
		current: current location (x,y)
		goals: 	 list of goal locations [(x1,y1),...,(xn,yn)]
		allowed: list of squares allowed to go
		"""
		actionSequence = []
        	print "----------------------------"
        	print current
        	print goals
		# TODO
		# dumb random actions for now
        	for i,g in enumerate(goals):
            		goals[i] = [g,0]
        	print "----------------------------"
        	print goals

        	#actionSequence = [random.choice(["Forward", "TurnLeft", "TurnRight", "Shoot", "Grab","Glimb"])]
        	problem = AstarSearch.AstarProblem([current,facing],goals,allowed)
        	search = AstarSearch.AstarSearch(problem)
        	actionSequence = search.run()
		return actionSequence

	### End Wumpus Hybrid Algorithm ###

	"""def search(self, environment, logicEngine): #TODO TODO TODO
		""
		Executes a logical search for the gold
		""
		self.environ = environment
		self.logic = logicEngine
		self.actions = 0
		self.hasArrow = True
		self.KB = KnowledgeBase.KnowledgeBase(self.logic)
		self.KB.initWumpusWorldLogic()
		success = False
		dead = False
		goldFound = False
		x, y = (0,0)

		#keep looking for the gold stupidly
		while not goldFound and not dead:

			#get percepts
			(breeze, stench, glitter) = self.environ.sense(x,y)

			dead = self.environ.isDeadly(x,y)

			if not dead:

				if glitter:
					goldFound = True

				else:
					#tell KB perception
					self.KB.tell(self.KB.makePerceptStatement([glitter, stench, breeze, False, False], self.actions))

					#get a list of adjacent cells
					adjacentCells = self.environ.proxy(x,y)

					#here is a good place to ask a query to the logic engine....
					query = "Safe(Pos(1,1))"
					isQueryProved = self.KB.ask(query)

					#pick one randomly
					(x, y) = random.choice(adjacentCells)

				#increment the action counter
				self.KB.tell(self.KB.makeActionStatement("Forward", self.actions))
				self.actions += 1

		return (success, dead, self.actions, self.hasArrow)"""