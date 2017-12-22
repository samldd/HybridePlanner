from __future__ import division
from wmi_experiment import main
import wmi_experiment
import time
from robot2_cont import *
import sys
import heuristic

# Versie met 2 queries in een WMI call


class Hplanner(object):

    timeWMC = 0
    timeFastSAT = 0
    timeGoalReached = 0
    nbWMICalls = 0

    def __init__(self, actions, init, goal):
        self.actions = actions
        self.init = init
        self.goal = goal
        heuristic.initialize(proposition_h, goal_h, init_h, actions_h)

    def start(self):
        """
            Voorlopig is er geen backtracking.. gready search
        """
        current = self.init
        while True:
            h_best = sys.maxint
            for n in self.generate_next_layer(current):
                sequence = n.get_prev_seq()
                sequence.remove("init")
                h = heuristic.get_heuristic_value(sequence, 0.85)
                print str(sequence) + " - " + str(h)
                if h == 0 and self.goal_reached(n):
                    return n
                if h < h_best:
                    h_best = h
                    current = n

    def generate_next_layer(self, node):
        new_layer = []
        for action in self.actions:
            l = action.copy()
            l.set_prev_layer(node)
            new_layer.append(l)
        return new_layer

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
        s += "\t(" + goal[0] + ").\n"
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
            Hplanner.nbWMICalls += 1
            p = main(s)
            p = p[0]/p[1]
        except:
            pass
        Hplanner.timeWMC += (time.time() - t)
        print p
        return p > 0.85

planner = Hplanner(actions, init, goal)

t = time.time()
print "\nAction sequence: {}\n".format(planner.start())
print "#############################"
print "Total runtime: {}".format(time.time()-t)
print "WMI time: {}".format(Hplanner.timeWMC)
print "Total SAT time: {}".format(wmi_experiment.intTime)
print "Total integration time: {}".format(wmi_experiment.integralTime)
print "Total WMI calls: {}".format(Hplanner.nbWMICalls)
print "#############################"