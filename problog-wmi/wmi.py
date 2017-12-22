from __future__ import print_function

import copy
import re
import time

import sympy
from scipy import integrate
from itertools import product as list_product

from problog.program import PrologString, PrologFile
from problog.formula import LogicDAG
from problog.evaluator import Semiring, FormulaEvaluatorNSP, FormulaEvaluator
from problog.sdd_formula import SDD


class Interval(object):
    def __init__(self, bounds, inclusive):
        self.bounds = bounds
        self.inclusive = inclusive

    def combine(self, interval):
        if self.bounds[0] > interval.bounds[0]:
            lower = (self.bounds[0], self.inclusive[0])
        elif self.bounds[0] < interval.bounds[0]:
            lower = (interval.bounds[0], interval.inclusive[0])
        else:
            lower = (self.bounds[0], self.inclusive[0] and interval.inclusive[0])

        if self.bounds[1] < interval.bounds[1]:
            upper = (self.bounds[1], self.inclusive[1])
        elif self.bounds[1] > interval.bounds[1]:
            upper = (interval.bounds[1], interval.inclusive[1])
        else:
            upper = (self.bounds[1], self.inclusive[1] and interval.inclusive[1])

        if lower > upper:
            print("\t\t\t", "INVALID", lower, upper)
            tmp = lower # TODO: aanpassing gemaakt
            lower = upper
            upper = tmp
        return Interval((lower[0], upper[0]), (lower[1], upper[1]))

    def __str__(self):
        left = "[" if self.inclusive[0] else "("
        right = "]" if self.inclusive[1] else ")"
        return left + str(self.bounds[0]) + "," + str(self.bounds[1]) + right

    def is_valid(self):
        return self.bounds[0] < self.bounds[1]


class EmptyInterval(Interval):
    def __init__(self, bounds, inclusive):
        Interval.__init__(self, (0, 0), (False, False))


class Intervals(object):
    def __init__(self, given):
        self.intervals = given

    def times(self, intervals):
        new = copy.copy(self.intervals)
        for v, i in intervals.intervals.items():
            new[v] = new[v].combine(i) if (v in new) else i
        return Intervals(new)

    def __str__(self):
        if len(self.intervals) == 0:
            return "Unbounded"
        return ", ".join(map(lambda t: t[0] + ":" + str(t[1]), self.intervals.items()))

    def keys(self):
        return self.intervals.keys()

    def bounds(self):
        l = []
        for v, i in self.intervals.items():
            l.append(list(i.bounds))
        return l

    def is_valid(self):
        return all(i.is_valid() for i in self.intervals.values())

    @classmethod
    def create(cls, string):
        if string == "boolean":
            return Intervals({})
        pattern = re.compile(r"(\w+)=([+-]?\d+\.?\d+?|\w+):([+-]?\d+\.?\d+?|\w+)")
        match = pattern.match(string)
        var = match.group(1)
        # inclusive = True if match.group(2) == "[" else False, True if match.group(5) == "]" else False
        bounds = float(match.group(2)), float(match.group(3))
        return Intervals({var: Interval(bounds, (True, True))})


class Formula(object):
    def __init__(self, formula):
        self.formula = formula

    def times(self, formula):
        return Formula(self.formula * formula.formula)

    def is_null(self):
        return self.formula == sympy.S(0.0)

    def __str__(self):
        return str(self.formula)

    @classmethod
    def create(cls, string):
        # parts = string.split("+")
        # formula = sympy.S(float(parts[0]))
        # pattern = re.compile(r"([+-]?\d+\.\d+)\*(\w+)")
        # for part in parts[1:]:
        #  match = pattern.match(part)
        #  formula = sympy.S(float(match.group(1))) * sympy.symbols(match.group(2))
        return Formula(sympy.sympify(string))


class Element(object):
    def __init__(self, list_of_tuples, key):
        # self.list = filter(lambda (i, e): not e.is_null(), list_of_tuples)
        self.list = list_of_tuples
        self.key = str(key)

    def times(self, element):
        combinations = list_product(self.list, element.list)
        if(self.key == "t"):
            key = element.key
        elif element.key == "t":
            key = self.key
        else:
            key = "(%s X %s)" %(self.key, element.key)
        product = Element(map(lambda ((i1, e1), (i2, e2)): (i1.times(i2), e1.times(e2)), combinations), key)
        return product

    def plus(self, element):
        if element.key == "!%s" %self.key or self.key == "!%s" %element.key:
            return Element([(Intervals({}), Formula(sympy.S(1.0)))], "t")
        if (self.key == "f"):
            key = element.key
        elif element.key == "f":
            key = self.key
        else:
            key = "(%s + %s)" %(self.key, element.key)
        combined = Element(self.list + element.list, key)
        # print self, " + ", element, " = ", sum
        return combined

    def integrate(self, operator):
        global integralTime
        result = operator.neutral_element
        for (i, f) in self.list:
            bounds = i.bounds()
            if not i.is_valid() or f.is_null() or any(map(lambda (b1, b2): b1 == b2, bounds)):
                integral = sympy.S(0.0)
            elif len(i.keys()) == 0:
                integral = f.formula
            else:
                keys = i.keys()
                f = sympy.lambdify(keys, f.formula)
                t = time.time()
                (integral, err) = integrate.nquad(f, bounds)
                integralTime = (time.time() - t)
                # print(integralTime)
                integral = sympy.S(integral)
            result = operator.perform(result, integral)
        print(self.key)
        return result

    def __str__(self):
        return " + ".join(map(lambda (i, f): "(" + str(i) + " | " + str(f) + ")", self.list))

        # return ",".join(map(lambda (i, f): str(f), self.list))

intTime = 0
integralTime = 0

class WmiSemiring(Semiring):
    def __init__(self, neutral):
        Semiring.__init__(self)
        self.neutral = neutral

    def zero(self):
        return Element([(Intervals({}), Formula(self.neutral))], "f")  # TODO empty intervals?

    def one(self):
        return Element([(Intervals({}), Formula(sympy.S(1.0)))], "t")

    def plus(self, a, b):
        #print("\t{} plus {}".format(a, b))
        return a.plus(b)

    def times(self, a, b):
        #print("\t\t{} times {} = {}".format(a, b, a.times(b)))
        return a.times(b)

    def pos_value(self, a, key=None):
        m = re.search(r"w\((.*),.*,(.*)\)", str(a))
        return Element([(Intervals.create(m.group(2)), Formula.create(m.group(1)))],key)

    def neg_value(self, a, key=None):
        m = re.search(r"w\(.*,(.*),(.*)\)", str(a)) # TODO: aanpassing
        return Element([(Intervals({}), Formula.create(m.group(1)))], "!" + str(key))
        # return Element([(Intervals.create(m.group(2)), Formula.create(m.group(1)))], "!" + str(key))

    def is_dsp(self):
        return True

    def is_nsp(self):
        return True

def solve(model, semiring, operator):
    t = time.time()
    if semiring.is_dsp():
        ev = SDD.create_from(model, label_all=True).to_formula()
        # for n, q in diagram.queries():
            # diagram.get_manager().write_to_dot(diagram.get_inode(q), "examples/formula" + str(q) + ".gv")
    else:
        ev = LogicDAG.create_from(model, label_all=True)
    if semiring.is_nsp():
        fe = FormulaEvaluatorNSP(ev, semiring)
    else:
        fe = FormulaEvaluator(ev, semiring)
    weights = ev.extract_weights(semiring=semiring)
    fe.set_weights(weights)
    result = {}
    print("inference time: {}".format(time.time()-t))
    for n, q in ev.queries():
        p = fe.evaluate(q)
        result[n] = (p, p.integrate(operator))


    return result


class Operator(object):
    def __init__(self, neutral_element, name):
        self.neutral_element = neutral_element
        self.name = name

    def perform(self, one, two):
        raise NotImplementedError("Perform is an abstract method")

    def get_neutral(self):
        return self.neutral_element

    def __str__(self):
        return self.name


class SumOperator(Operator):
    def __init__(self):
        Operator.__init__(self, sympy.S(0.0), "sum")

    def perform(self, one, two):
        return one + two


class MaxOperator(Operator):
    def __init__(self):
        Operator.__init__(self, -sympy.oo, "max")

    def perform(self, one, two):
        return max(one, two)


class MinOperator(Operator):
    def __init__(self):
        Operator.__init__(self, sympy.oo, "min")

    def perform(self, one, two):
        return min(one, two)


def main(file):
    pl = PrologString(file)
    # pl = PrologFile(file)
    operator = SumOperator()
    result = solve(pl, WmiSemiring(operator.neutral_element), operator)
    for k, v in result.items():
        (formula, integral) = v
        # print('%s(%s): %s\n%s' % (operator, k, integral, formula))
        # print(formula.key)
    return integral


def argparser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    return parser

if __name__ == '__main__':
    pl = PrologFile("prpg")
    t = time.time()
    operator = SumOperator()
    result = solve(pl, WmiSemiring(operator.neutral_element), operator)
    for k, v in result.items():
        (formula, integral) = v
        print(formula)
    print("total time: {}".format(time.time()-t))
    print(integral)


"""def main():
   intervals1 = Intervals({"x": Interval((0, 10), (True, False)), "a": Interval((-5, 5), (True, True))})
   intervals2 = Intervals({"x": Interval((5, 10), (True, True)), "b": Interval((-5, 5), (True, True))})
   intervals = intervals1.times(intervals2)
   print(intervals)
   f = Formula(4, {"x": 5})
   print(f)

if __name__ == '__main__':act
   main()
"""
