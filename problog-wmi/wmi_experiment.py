from __future__ import print_function

import copy
import re
import time

import sympy
from sympy import Symbol, Float
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
        pattern = re.compile(r"(\w+)=([+-]?\d+\.?\d+?):([+-]?\d+\.?\d+?)")
        match = pattern.match(string)
        var = match.group(1)
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
        return Formula(sympy.sympify(string))


class Element(object):
    def __init__(self, list_of_tuples, key):
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



    def inte(self, formula, bounds, keys):
        # print(formula)
        coeff = formula.as_ordered_factors()
        res = 1
        for i in range(0,len(coeff)):
            if type(coeff[i]) == Float:
                res *= float(coeff[i])
            elif type(coeff[i]) == Symbol:
                j = keys.index(str(coeff[i]))
                keys.pop(j)
                bound = bounds.pop(j)
                res *= ((bound[1]**2 - bound[0]**2) / 2)
            else:
                j = keys.index(str(coeff[i]._args[0]))
                keys.pop(j)
                bound = bounds.pop(j)
                c = int(coeff[i]._args[1]) + 1
                res *= ((bound[1]**c - bound[0]**c) /c)
        for b in bounds:
            res *= (b[1]-b[0])
        return res


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
                func = f.formula
                f = sympy.lambdify(keys, func)
                t = time.time()
                # (integral, err) = integrate.nquad(f, bounds)
                integral = self.inte(func, bounds, keys)
                integralTime += (time.time() - t)
                integral = sympy.S(integral)
            result = operator.perform(result, integral)

        return result

    def __str__(self):
        return " + ".join(map(lambda (i, f): "(" + str(i) + " | " + str(f) + ")", self.list))

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
        return a.plus(b)

    def times(self, a, b):
        return a.times(b)

    def pos_value(self, a, key=None):
        m = re.search(r"w\((.*),.*,(.*)\)", str(a))
        return Element([(Intervals.create(m.group(2)), Formula.create(m.group(1)))],key)

    def neg_value(self, a, key=None):
        m = re.search(r"w\(.*,(.*),(.*)\)", str(a))
        return Element([(Intervals({}), Formula.create(m.group(1)))], "!" + str(key))

    def is_dsp(self):
        return True

    def is_nsp(self):
        return True

def solve(model, semiring, operator):
    global intTime
    t = time.time()
    if semiring.is_dsp():
        ev = SDD.create_from(model, label_all=True).to_formula()
    else:
        ev = LogicDAG.create_from(model, label_all=True)
    if semiring.is_nsp():
        fe = FormulaEvaluatorNSP(ev, semiring)
    else:
        fe = FormulaEvaluator(ev, semiring)
    intTime += (time.time() - t)
    weights = ev.extract_weights(semiring=semiring)
    fe.set_weights(weights)
    result = {}
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
    integrals = []
    for k, v in result.items():
        (formula, integral) = v
        integrals.append(integral)
        # print(integral)
        # print('%s(%s): %s\n%s' % (operator, k, integral, formula))
        #print(formula.key)
    return integrals


def argparser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    return parser

if __name__ == '__main__':
    s=open("CNF_cont").read()
    t = time.time()
    for _ in range(0,50):
        main(s)
    print((time.time()-t)/50)