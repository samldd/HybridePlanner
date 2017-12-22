import sympy


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