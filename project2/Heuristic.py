#!/usr/bin/env python

class Heuristic:
	"""Heuristic is a class that stores a heuristic function for a particular Problem instance.
	   This class contains the two heuristics: admissible and non-admissible."""
	goalState = ["","",""] 
	heuristicType = 0

	def __init__(self, heuristicType, goalState):
		self.heuristicType = heuristicType
		self.goalState = goalState

	def h(self, state):
		"""Evaluates a heuristic function. Specify type of heuristic to use."""
		if self.heuristicType == 1: # Admissible
			return self.heuristicFunction1(state)
		elif self.heuristicType == 2: # Non-admissible
			return self.heuristicFunction2(state)
		else:
			return 0 # no heuristic

	def heuristicFunction1(self, state):
		"""Returns the heuristic function value evaluated at current state."""
		value = 0
		for curr, goal in zip(state, self.goalState):
			for a, b in zip(curr, goal):
				if a == b:
					value += 1	
		return value

	def heuristicFunction2(self, state):
		"""Returns the heuristic function value evaluated at current state."""
		return 0
