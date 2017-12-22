from __future__ import division
from wmi_experiment import main
import wmi_experiment
import time
from robot2_cont import *
from DBN import *
import sys

# Versie met 2 queries in een WMI call

class ID(object):

    timeWMC = 0
    timeFastSAT = 0
    timeGoalReached = 0
    nbWMICalls = 0

    def __init__(self, actions, init, goal):
        self.actions = actions
        self.init = init
        self.goal = goal

    def start(self):
        if self.goal_reached(self.init):
            return init
        for i in range(1,6):
            time1 = time.time()
            result = self.start_it(self.init, i)
            print "step" + str(i) + " time: " + str(time.time()-time1)
            if result:
                return result

    def start_it(self, node, depth):
        # print depth
        if depth <= 0:
            if self.goal_reached(node):
                return node
            return None
        for action in self.actions:
            l = action.copy()
            l.set_prev_layer(node)
            result = self.start_it(l, depth-1)
            if result:
                return result

    def sentence(self, propositions, clauses, goal):
        s = ""
        for p in propositions:
            s += p + "\n"
        s += "\nf :- \n"
        for i in range(0, len(clauses) - 1):
            s += "\t(" + clauses[i] + "),\n"
        s += "\t(" + clauses[len(clauses) - 1] + ").\n"
        s += "\n"
        s += "g:- f,"
        for i in range(0,len(goal)-1):
            s += "\t(" + goal[i] + "),\n"
        s += "\t(" + goal[-1] + ").\n"
        s += "query(g).\n"
        s += "query(f).\n"
        return s

    def goal_reached(self, node):
        # print node
        (propositions, clauses, _) = node.convert(0)
        goal_clause = node.convert_goal(goal)
        s = self.sentence(propositions, clauses, goal_clause)
        p = 0
        t = time.time()
        try:
            ID.nbWMICalls += 1
            p = main(s)
            p = p[0]/p[1]
            # open("CNF", "w").write(s)
        except:
            pass
        ID.timeWMC += (time.time() - t)
        return p > 0.85

b = ID(actions, init, goal)
t = time.time()
print "\nAction sequence: {}\n".format(b.start())

print "#############################"
print "Total runtime: {}".format(time.time()-t)
print "WMI time: {}".format(ID.timeWMC)
print "Total SAT time: {}".format(wmi_experiment.intTime)
print "Total integration time: {}".format(wmi_experiment.integralTime)
print "Total WMI calls: {}".format(ID.nbWMICalls)
print "#############################"