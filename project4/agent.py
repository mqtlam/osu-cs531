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

	def printMap(self,xa,ya,f):

		for y in range(self.environ.size-1, -1, -1):
			for x in range(0, self.environ.size):

				(pit,wumpus,gold) = (False, False, False)
				agent = False

				if (x,y) in self.environ.map:
					(pit,wumpus,gold) = self.environ.map[(x,y)]

                		if (x,y) == (xa,ya):
                    			agent = True
				if f == 0:
					f = "N"
				if f == 1:
					f = "E"
				if f == 2:
					f = "S"
				if f == 3:
					f = "W"

				print ("%s%s%s%s |" % ( "p" if pit else " ", "w" if wumpus else " ", "g" if gold else " ", "a"+f if agent else " " )),

			print ""

			#print a row seperator
			print "_____ " * self.environ.size

	def search(self, environment, logicEngine):
		"""
		Runs the program loop.
		"""
		self.environ = environment
		self.logic = logicEngine
		self.hasArrow = True
		self.rewards = 0
        	self.steps = 0

		success = False
		dead = False
		haveGold = False
		x, y = (0,0)
		facing = NORTH

		# persistent agent variables
		self.KB = KnowledgeBase.KnowledgeBase(self.logic, self.environ)
		self.KB.initWumpusWorldLogic()
		self.timer = 0 # timer
		self.plan = [] # action sequence

		# "hack" to include these percepts for environment
		scream = False
		bump = False

		while not success and not dead:
            		print '--------------------------------'
            		print '(x,y):'
            		print (x,y)
			self.printMap(x,y,facing)

			# get percepts
			(breeze, stench, glitter) = self.environ.sense(x,y)

			dead = self.environ.isDeadly(x,y)

			if not dead:
				action = self.hybridWumpusAgent([glitter, stench, breeze, bump, scream], (x, y), facing, self.hasArrow, haveGold)
				self.rewards = self.rewards - len(action)
				self.steps = self.steps + len(action)

				if bump:
					bump = False
				if scream:
					scream = False

				if action == "Forward":
					if facing == NORTH:
						bump = not self.environ.canMove(x, y+1)
						if not bump:
							(x, y) = (x, y+1)
					if facing == EAST:
						bump = not self.environ.canMove(x+1, y)
						if not bump:
							(x, y) = (x+1, y)
					if facing == SOUTH:
						bump = not self.environ.canMove(x, y-1)
						if not bump:
							(x, y) = (x, y-1)
					if facing == WEST:
						bump = not self.environ.canMove(x-1, y)
						if not bump:
							(x, y) = (x-1, y)
				elif action == "TurnLeft":
					facing = (facing - 1) % 4
				elif action == "TurnRight":
					facing = (facing + 1) % 4
				elif action == "Shoot" and self.hasArrow:
					print "used shoot action"
					wumpusHit = self.environ.shootArrow(x, y, facing)
					self.hasArrow = False
					if wumpusHit:
						scream = True
					self.rewards = self.rewards + 100
				elif action == "Grab":
					print "used grab action"
					if glitter and not haveGold:
						haveGold = True
					self.rewards = self.rewards + 500
				elif action == "Climb":
					print "used climb action"
					if (x, y) == (0, 0) and haveGold:
						success = True
					else:
						success = False
						break
					self.rewards = self.rewards + 200

		return (success, dead, self.timer, self.hasArrow, self.rewards, self.steps, haveGold)

	### Wumpus Hybrid Algorithm ###

	def hybridWumpusAgent(self, percept, current, facing, hasArrow, haveGold):
		"""
		Main logic algorithm.
		percept is a list of True/False: [glitter, stench, breeze, bump, scream]
		"""
		self.KB.tell("%% === time %d ===" % self.timer)
		self.KB.tell("%% === time %d ===" % self.timer, True)
		# tell agent the percepts and therefore breezy, smelly
		self.KB.tellAssumptionsAtTime(percept, self.timer, current, hasArrow, haveGold)

		# tell agent update of world
		self.KB.tellUsableAtTime(self.timer, current)

		# get all squares that are safe
		safe = [(x,y) for x in range(0, self.environ.size) for y in range(0, self.environ.size) if self.KB.ask("OK(%d,%d,%d)" % (x,y,self.timer))]
		print "OK", safe

		unvisited = []
		if self.KB.ask("Glitter(%d) & -HaveGold(%d)" % (self.timer, self.timer)):
			self.plan = ["Grab"] + self.planRoute(current, facing, [(0,0)], safe, False) + ["Climb"]

		if self.plan == []:
            		print '=== No Glitter, find a safe unvisited square.'
			unvisited = [(x,y) for x in range(0, self.environ.size) for y in range(0, self.environ.size) if all([not self.KB.ask("Loc(%d,%d,%d)" % (x,y,t)) for t in range(0,self.timer+1)])]
			self.plan = self.planRoute(current, facing, list(set(unvisited).intersection(set(safe))), safe, False)

		if self.plan == [] and self.KB.ask("HaveArrow(%d)" % self.timer):
            		print '=== No unvisited square, take a possible wumpus square.'
			possibleWumpus = [(x,y) for x in range(0, self.environ.size) for y in range(0, self.environ.size) if not self.KB.ask("-W(%d,%d)" % (x,y))]
			self.plan = self.planRoute(current, facing, possibleWumpus, safe, True)

		if self.plan == []: # no choice, but to take a risk
            		print '=== No wumpus found, find an unvisited but unsafe one.'
			notUnsafe = [(x,y) for x in range(0, self.environ.size) for y in range(0, self.environ.size) if not self.KB.ask("-OK(%d,%d,%d)" % (x,y,self.timer))]
			self.plan = self.planRoute(current, facing, list(set(unvisited).intersection(set(notUnsafe))), safe, False)

		if self.plan == []:
            		print '=== Nothing plan, just climb out.'
			self.plan = self.planRoute(current, facing, [(0,0)], safe, False) + ["Climb"]

		print "ACTION PLAN: ", self.plan

		action = self.plan.pop(0)

		self.KB.tell(self.KB.makeActionStatement(action, self.timer))
		self.timer += 1

		return action

	def planRoute(self, current, facing, goals, allowed, shoot):
		"""
		Plan a route. Calls A*.
		current: current location (x,y)
		goals: 	 list of goal locations [(x1,y1),...,(xn,yn)]
		allowed: list of squares allowed to go
        shoot: PlanShoot if True, PlanRoute else
		"""
		actionSequence = []
		allowed = list(set(allowed).union(set(goals)))

        	#actionSequence = [random.choice(["Forward", "TurnLeft", "TurnRight", "Shoot", "Grab","Glimb"])]
        	problem = AstarSearch.AstarProblem([current,facing],goals,allowed)
        	search = AstarSearch.AstarSearch(problem,shoot)
        	actionSequence = search.run()
                #problem = RBFSSearch.RBFSProblem([current,facing],goals,allowed)
                #search = RBFSSearch.RBFSSearch(problem,shoot)
            #actionSequence = search.run()
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
