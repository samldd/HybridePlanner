
class Node(object):

    def __init__(self, name):
        self.parents = {}
        self.name = name

    def add_parent(self, parent):
        self.parents[parent.name] = parent

    def get_parent(self, parent):
        return self[parent]

    def get_CPT(self):
        return self.CPT

    def set_CPT(self, cpt):
        self.CPT = cpt

    def convert(self, literals, clause):
        self.CPT.convert(literals, clause)

class CPT(object):

    def __init__(self, node, values, intervals):
        self.node = node
        self.columns = values
        self.intervals = intervals
        self.rows = {}

    def add_row(self, cond, row):
        self.rows[cond] = row

    def convert(self, literals, clause):
        mutex = "("
        for i in range(0, len(self.columns)-1):
            mutex += self.columns[i] + " ; "
        mutex += self.columns[-1] + "),"
        clause.append(mutex)
        for i in range(0, len(self.columns)):
            literals+= ["w(1, 1, {0})::{1}.".format(self.intervals[i], self.columns[i])]
            for j in range(i+1, len(self.columns)):
                clause.append("(not {0} ; not {1}),".format(self.columns[i], self.columns[j]))
        rownb = 0
        for cond in self.rows:
            rownb += 1
            ksi = "("
            for c in cond.split(","):
                if not c: break
                ksi += "not {} ; ".format(c)
            if "1" in self.rows[cond]:
                clause.append(ksi + self.columns[self.rows[cond].index("1")] + "),")
                continue
            for i in range(0, len(self.rows[cond])):
                literals += ["w({0}, 1, boolean)::{1}.".format(self.rows[cond][i], self.columns[i] + "_{}".format(rownb))]
                clause.append(ksi + "not {0}_{1} ; {2}),".format(self.columns[i], rownb, self.columns[i]))
            mutex = ksi
            for i in range(0, len(self.rows[cond]) - 1):
                mutex +=  self.columns[i] + "_{}".format(rownb) + " ; "
            mutex += self.columns[-1] + "_{}".format(rownb) + "),"
            clause.append(mutex)

