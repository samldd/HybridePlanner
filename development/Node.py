
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


x0 = Node("X_0")
x0_cpt = CPT(x0, ["i1_0", "i2_0", "i3_0", "i4_0"],
                 ["x0=0.0:1.0", "x0=1.0:2.0", "x0=2.0:3.0", "x0=3.0:4.0"])
x0_cpt.add_row("", ["x0", "2-x", "0", "0"])
x0.set_CPT(x0_cpt)

eps1 = Node("eps_1")
eps1_cpt = CPT(eps1, ["e1_1", "e2_1", "e3_1"],
                    ["y0=0.0:1.0", "y0=1.0:2.0", "boolean"])
eps1_cpt.add_row("i1_0", ["y0", "2-y0", "0"])
eps1_cpt.add_row("i2_0", ["1.5*y0", "1-0.5*y0", "0"])
eps1_cpt.add_row("i3_0", ["0", "0", "1"])
eps1_cpt.add_row("i4_0", ["0", "0", "1"])
eps1.set_CPT(eps1_cpt)
eps1.add_parent(x0)

x1 = Node("X_1")
x1_cpt = CPT(x0, ["i1_1", "i2_1", "i3_1", "i4_1"],
                 ["x1=0.0:1.0", "x1=1.0:2.0", "x1=2.0:3.0", "x1=3.0:4.0"])
x1_cpt.add_row("i1_0,e1_1", ["2*Piecewise((x1-y0, (0<x1-y0) & (x1-y0<1)), ( 0, True ))", "2*Piecewise((x1-y0, (0<x1-y0) & (x1-y0<1)), ( 0, True ))", "2*Piecewise((x1-y0, (0<x1-y0) & (x1-y0<1)), ( 0, True ))", "2*Piecewise((x1-y0, (0<x1-y0) & (x1-y0<1)), ( 0, True ))"])
x1_cpt.add_row("i1_0,e2_1", ["2*Piecewise((x1-y0, (0<x1-y0) & (x1-y0<1)), ( 0, True ))", "2*Piecewise((x1-y0, (0<x1-y0) & (x1-y0<1)), ( 0, True ))", "2*Piecewise((x1-y0, (0<x1-y0) & (x1-y0<1)), ( 0, True ))", "2*Piecewise((x1-y0, (0<x1-y0) & (x1-y0<1)), ( 0, True ))"])
x1_cpt.add_row("i2_0,e1_1", ["2*Piecewise((2-(x1-y0),(1<x1-y0) & (x1-y0<2)), ( 0, True ))", "2*Piecewise((2-(x1-y0),(1<x1-y0) & (x1-y0<2)), ( 0, True ))", "2*Piecewise((2-(x1-y0),(1<x1-y0) & (x1-y0<2)), ( 0, True ))", "2*Piecewise((2-(x1-y0),(1<x1-y0) & (x1-y0<2)), ( 0, True ))"])
x1_cpt.add_row("i2_0,e2_1", ["2*Piecewise((2-(x1-y0),(1<x1-y0) & (x1-y0<2)), ( 0, True ))", "2*Piecewise((2-(x1-y0),(1<x1-y0) & (x1-y0<2)), ( 0, True ))", "2*Piecewise((2-(x1-y0),(1<x1-y0) & (x1-y0<2)), ( 0, True ))", "2*Piecewise((2-(x1-y0),(1<x1-y0) & (x1-y0<2)), ( 0, True ))"])
x1_cpt.add_row("i3_0,e3_1", ["0", "0", "1", "0"])
x1_cpt.add_row("i4_0,e3_1", ["0", "0", "0", "1"])
x1.set_CPT(x1_cpt)
x1.add_parent(eps1)
x1.add_parent(x0)

def print_list(l):
    for e in l:
        print e

literals = []
clauses = []
x0.convert(literals, clauses)
eps1.convert(literals, clauses)
x1.convert(literals, clauses)
print_list(literals)
print_list(clauses)