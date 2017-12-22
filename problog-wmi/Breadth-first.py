import copy
import os
from wmi import main

class BreadthFirst(object):

    def __init__(self, actions, init, goal):
        self.actions = actions
        self.leafs = [init]
        self.goal = goal
        t = self.leafs[0].replace(0)
        self.times = [t]

    def start(self):
        if self.goal_reached(self.leafs[0]):
            return init
        result = None
        while result == None:
            result = self.step()
        return result

    def step(self):
        self.leafs = nodes = self.generate_next_layer()
        for n in nodes:
            if self.goal_reached(n):
                return n
        return None

    def generate_next_layer(self):
        new_layer = []
        new_t = []
        for i in range(0,len(self.leafs)):
            for action in self.actions:
                l = action.copy()
                l.set_prev_layer(self.leafs[i])
                new_layer.append(l)
                new_t.append(l.replace(self.times[i]))
        self.times = new_t
        return new_layer

    p = 0

    def goal_reached(self, node):
        print node
        (propositions, clauses) = node.convert()
        theGoal = copy.deepcopy(self.goal)
        for g in theGoal:
            g.parent = node.get(g.parent)
        f = open("CNF", "w")
        for p in propositions:
            f.write(p + "\n")
        f.write("\nf :- \n")
        for g in theGoal:
            f.write("\t(" + str(g) + "),\n")
        for i in range(0, len(clauses) - 1):
            f.write("\t(" + clauses[i] + "),\n")
        f.write("\t(" + clauses[len(clauses) - 1] + ").\n")
        f.write("\n")
        f.write("query(f).\n")
        f.close()
        p = 0
        try:
            p = main("CNF")
        except Exception: pass
        os.remove("CNF")
        return p > 0.70


from robot2 import actions, init, goal
b = BreadthFirst(actions, init, goal)
print b.start()
