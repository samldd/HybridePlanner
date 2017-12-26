import time
from itertools import product as list_product

import sympy

from formula import Formula
from intervals import Intervals
from skmonaco import mcquad

integralTime = 0

class Element(object):

    dict = {}

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
                t = time.time()
                keys = i.keys()
                for symb in set(map(lambda x: str(x), f.formula.free_symbols)) & set(Element.dict.keys()):
                    f.formula = f.formula.subs(sympy.Symbol(symb),
                                               sympy.sympify(Element.dict[symb]))
                # print(f.formula)
                # print(keys)
                # print(bounds)
                f = sympy.lambdify(keys, f.formula)
                xl = map(lambda x: x[0],bounds)
                xu = map(lambda x: x[1], bounds)
                (integral, err) = mcquad(lambda x: apply(f,x), 100, xl, xu)
                integral = sympy.S(integral)
                # print(integral)
                # print("integration time: {}".format(time.time()-t))
            result = operator.perform(result, integral)
        return result

    def __str__(self):
        return " + ".join(map(lambda (i, f): "(" + str(i) + " | " + str(f) + ")", self.list))
        # return ",".join(map(lambda (i, f): str(f), self.list))