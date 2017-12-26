import re

import sympy
from element import Element
from formula import Formula
from problog.evaluator import Semiring

from intervals import Intervals

debug = False

class WmiSemiring(Semiring):
    def __init__(self, neutral):
        Semiring.__init__(self)
        self.neutral = neutral

    def zero(self):
        return Element([(Intervals({}), Formula(self.neutral))], "f")  # TODO empty intervals?

    def one(self):
        return Element([(Intervals({}), Formula(sympy.S(1.0)))], "t")

    def plus(self, a, b):
        if debug:
            print("\t{} plus {}".format(a, b))
        return a.plus(b)

    def times(self, a, b):
        if debug:
            print("\t\t{} times {} = {}".format(a, b, a.times(b)))
        return a.times(b)

    def pos_value(self, a, key=None):
        m = re.search(r"w\((.*),.*,(.*)\)", str(a))
        return Element([(Intervals.create(m.group(2)), Formula.create(m.group(1)))], key)

    def neg_value(self, a, key=None):
        m = re.search(r"w\(.*,(.*),(.*)\)", str(a)) # TODO: aanpassing
        return Element([(Intervals({}), Formula.create(m.group(1)))], "!" + str(key))
        # return Element([(Intervals.create(m.group(2)), Formula.create(m.group(1)))], "!" + str(key))

    def is_dsp(self):
        return True

    def is_nsp(self):
        return True