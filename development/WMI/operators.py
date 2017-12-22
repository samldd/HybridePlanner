import sympy


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