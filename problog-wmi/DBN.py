class Node(object):
    def __init__(self, name, columns, rows):
        self.name = name
        self.columns = columns
        self.rows = rows

    def get_name(self):
        return self.name

    def convert(self, t, layer):
        propositions = []
        columns = []
        clauses = []
        told = t
        # every z in Z: state proposition
        for i in range(0, len(self.columns)):
            propositions.append("w(1,1,boolean)::x{}.".format(t))
            columns.append("x{}".format(t))
            t += 1
        # exactly one relation
        s = "x" + str(told)
        for i in range(told + 1, t):
            s += " ; x{}".format(i)
        if len(self.columns) > 1:  # No boolean variable
            clauses.append(s)
        for i in range(told, t):
            j = i + 1
            while j < t:
                clauses.append("not x{0} ; not x{1}".format(i, j))
                j += 1
        # Conversion of each row in the CPT
        for row in self.rows:
            t = row.convert(propositions, clauses, layer, columns, t)
        self.columns = columns
        return propositions, clauses, t

    def get(self, item):
        return self.columns[item]


class Row(object):
    def __init__(self, condition, values):
        self.conditions = condition
        self.values = values

    def get_cond(self, layer):
        # Bouw conditie op
        if len(self.conditions) != 0:
            cond = (-self.conditions[0]).convert(layer) + " ; "
            for j in range(1, len(self.conditions)):
                cond += (-self.conditions[j]).convert(layer) + " ; "
        else:
            cond = ""
        return cond


class CRow(Row):
    def convert(self, propositions, clauses, layer, columns, t):
        told = t
        for i in range(0, len(self.values)):
            func = self.values[i].replace("x", "x{}".format(layer.depth))
            propositions.append("w({0},1,x{1}={2:1.1f}:{3:1.1f})::wx{4}.".format(func,layer.depth,i,i+1, t))
            t += 1
        cond = self.get_cond(layer)
        for i in range(told, t):
            s = cond
            j = told
            while j < i:
                s += "wx{} ; ".format(j)
                j += 1
            s += "not wx{}".format(i) + " ; " + columns[i - told]
            clauses.append(s)
        s = cond + "wx{}".format(told)
        for i in range(told + 1, t):
            s += " ; wx{}".format(i)
        clauses.append(s)
        return t


class DRow(Row):
    def convert(self, propositions, clauses, layer, columns, t):
        cond = self.get_cond(layer)
        for i in range(0, len(self.values)):
            if self.values[i] == "1":  # Ga op zoek naar de 1
                clauses.append(cond + columns[i])
        return t


class BRow(Row):
    def convert(self, propositions, clauses, layer, columns, t):
        cond = self.get_cond(layer)
        if self.values[0] == "1":  # Ga op zoek naar de 1
            clauses.append(cond + columns[0])
        else:
            clauses.append(cond + "not " + columns[0])
        return t


class Literal(object):
    def __init__(self, parent, element, val=True):
        self.parent = parent
        self.val = val
        self.element = element

    def convert(self, layer):
        if not self.val:
            return "not {}".format(layer.get_prev(self.parent).get(self.element))
        return str(layer.get_prev(self.parent).get(self.element))

    def __neg__(self):
        return Literal(self.parent, self.element, not self.val)


class Layer(object):
    def __init__(self, variables, name, action=None):
        self.actionNode = action
        self.variables = variables
        self.prevLayer = None
        self.depth = 0
        self.name = name

    def set_prev_layer(self, previous):
        self.depth = previous.depth + 1
        self.prevLayer = previous

    def get_prev(self, name):
        for v in self.prevLayer.variables:
            if v.get_name() == name:
                return v
        if self.actionNode.get_name() == name:
            return self.actionNode

    def get(self, name):
        for v in self.variables:
            if v.get_name() == name:
                return v

    def convert_goal(self, goals):
        c = []
        for g in goals:
            if not g.val:
                c.append("not " + self.get(g.parent).get(g.element))
            else:
                c.append(self.get(g.parent).get(g.element))
        return c

    def convert(self, t):
        proposition = []
        clauses = []
        if self.prevLayer:
            (p, c, t) = self.prevLayer.convert(t)
            proposition += p
            clauses += c
        if self.actionNode:
            (p, c, t) = self.actionNode.convert(t, self)
            proposition += p
            clauses += c
        for v in self.variables:
            (p, c, t) = v.convert(t, self)
            proposition += p
            clauses += c
        return proposition, clauses, t

    def copy(self):
        return Layer(self.variables, self.name, self.actionNode)

    def get_prev_seq(self):
        if self.prevLayer:
            seq = self.prevLayer.get_prev_seq()
            seq.append(self.name)
            return seq
        return [self.name]

    def __str__(self):
        if self.prevLayer:
            return self.name + " " + str(self.prevLayer)
        else:
            return self.name