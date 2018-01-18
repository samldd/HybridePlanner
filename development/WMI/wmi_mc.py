from __future__ import print_function

import time

from operators import SumOperator
from problog.evaluator import FormulaEvaluatorNSP, FormulaEvaluator
from problog.formula import LogicDAG
from problog.program import PrologString
from problog.sdd_formula import SDD

from wmi_semiring import WmiSemiring


def solve(model, semiring, operator):
    ev = SDD.create_from(model, label_all=True).to_formula() if semiring.is_dsp() else LogicDAG.create_from(model, label_all=True)
    fe = FormulaEvaluatorNSP(ev, semiring) if semiring.is_nsp() else FormulaEvaluator(ev, semiring)
    weights = ev.extract_weights(semiring=semiring)
    fe.set_weights(weights)
    result = {}

    for n, q in ev.queries():
        p = fe.evaluate(q)
        result[n] = (p, p.integrate(operator))
    return result


def transform(s):
    from element import Element
    import re
    sub = "(?:\(.+\))+"
    pattern = u"(Piecewise\({}\))".format(sub)
    dict = {}
    for i,p in enumerate(set(re.findall(pattern, s))):
        new = "z{}".format(i)
        dict[new] = p
        s = s.replace(p, new)
    Element.dict = dict
    return s


def main(string):
    string = transform(string)
    pl = PrologString(string)
    operator = SumOperator()
    result = solve(pl, WmiSemiring(operator.neutral_element), operator)
    for k, v in result.items():
        (formula, integral) = v
    #     print('%s(%s): %s\n%s' % (operator, k, integral, formula))
    #     print(formula.key)
    return integral


if __name__ == '__main__':
    string = open("examples/debug").read()
    t = time.time()
    print("result={}".format(main(string)))
    print("time: {}s".format(time.time()-t))
