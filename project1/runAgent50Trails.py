#!/usr/bin/env python
from MemorylessAgent import *
from RandomizedAgent import *
from ModelBasedAgent import *
from Environment import *

import sys
import random
import pylab

## Process command line arguments

def printUsage():
	print 'Usage: ' + sys.argv[0] + ' 1|2|3 [n m p]'
	print '\t1 = memoryless, 2 = randomized, 3 = model-based'
	print '\tn by m grid with p probability (0.0-1.0)'

if len(sys.argv) < 2:
	printUsage()
	sys.exit(1)

agent_type = int(sys.argv[1])
agent = None
if agent_type == 1:
	agent = MemorylessAgent()
elif agent_type == 2:
	agent = RandomizedAgent()
elif agent_type == 3:
	agent = ModelBasedAgent()
else:
	printUsage()
	sys.exit(2)

n = int(sys.argv[2]) if len(sys.argv) > 2 else 10 # columns
m = int(sys.argv[3]) if len(sys.argv) > 3 else 10 # rows
p = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0 # probability of dirt

if n <= 0 or m <= 0:
	printUsage()
	sys.exit(3)

if p < 0.0 or p > 1.0:
	printUsage()
	sys.exit(4)

all_num_clean_cells = []
number_actions_to_take = []
for i in range(50):
    print "\n\n\n"
    print "******************************%d***************************************" % i
    ## Set up world environment
    environment = Environment(n, m, p)

    ## Main loop
    MAX_ACTIONS = 8000 # prevent from running forever
    num_actions = 0
    num_clean_cells = []
    running = True
    while (running and num_actions < MAX_ACTIONS):
        # print current world
        #print "Action " + str(num_actions)
        #environment.printCurrentWorld()

        # set up percept
        percept = environment.getPercept()

        # agent performs a step
        action = agent.takeStep(percept)
        print "---Action %d has been taken---" % action

        # update environment and counters
        running = environment.updateWorld(action)
        num_actions += 1

        # print num actions & num clean cells
        num_clean_cells.append(environment.getNumCleanCells())
        print "* " + str(num_actions) + ", " + str(num_clean_cells[num_actions-1])

        # for randomized agent experiments
        if num_clean_cells[num_actions-1] >= int(n*m*0.90):
            running = 0

        ## Results
        #print "Number of actions: " + str(num_actions)
        #print "Number of clean cells: " + str(num_clean_cells) + "/" + str(n*m)
        #environment.performance(num_clean_cells, 1)

    all_num_clean_cells.append(num_clean_cells)
    number_actions_to_take.append(num_actions-1)

    pylab.plot(range(1,len(num_clean_cells)+1), num_clean_cells)

pylab.xlabel('number of actions')
pylab.ylabel('number of clean cells')
pylab.title('performance curve')
pylab.grid(True)
pylab.show()
