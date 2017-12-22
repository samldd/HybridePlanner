import copy
from wmi import main
import wmi
import time
import pycosat

class ID(object):

    timeWMC = 0
    timeFastSAT = 0
    timeGoalReached = 0

    def __init__(self, actions, init, goal):
        self.actions = actions
        self.init = init
        self.goal = goal

    def start(self):
        t = self.init.replace(1)
        if self.goal_reached(self.init):
            return init
        for i in range(6,8):
            time1 = time.time()
            result = self.start_it(self.init, t, i)
            print "step" + str(i) + " time: " + str(time.time()-time1)
            if result:
                print "WMC time: " + str(ID.timeWMC)
                return result


    def start_it(self, node, time, depth):
        # print depth
        for action in self.actions:
            t = int(time)
            l = action.copy()
            l.set_prev_layer(node)
            t = l.replace(t)
            if self.goal_reached(l):
                return l
            elif depth-1 <= 0:
                return None
            elif self.start_it(l, t, depth-1):
                return node


    def goal_reached(self, node):
        (propositions, clauses) = node.convert()
        theGoal = copy.deepcopy(self.goal)
        # t = time.time()
        for g in theGoal:
            g.parent = node.get(g.parent)
        cnf = []
        for g in theGoal:
            cnf.append([int(str(g).replace("not ","-").replace("x",""))])
        for i in range(0, len(clauses) - 1):
            row = clauses[i].replace("wx","").replace("x","").replace("not ","-").replace("_","512").split(";")
            newrow = []
            for e in row:
                newrow.append(int(e))
            cnf.append(newrow)
        sat = pycosat.solve(cnf)
        # ID.timeFastSAT += (time.time() - t)
        if sat == "UNSAT":
            return False

        s = ""
        for p in propositions:
            s += p + "\n"
        s += "\nf :- \n"
        for g in theGoal:
            s += "\t(" + str(g) + "),\n"
        for i in range(0, len(clauses) - 1):
            s += "\t(" + clauses[i] + "),\n"
        s += "\t(" + clauses[len(clauses) - 1] + ").\n"
        s += "\n"
        s += "query(f).\n"
        p = 0
        t = time.time()
        try:
            p = main(s)
            # if p > 0.30:
            #     f = open("CNF", "w")
            #     f.write(s)
            #     f.close()

        except Exception:
            pass
        ID.timeWMC += (time.time() - t)
        return p > 0.30


from robot2 import actions, init, goal

b = ID(actions, init, goal)
t = time.time()
print b.start()
print time.time()-t