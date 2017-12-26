from __future__ import print_function

import time

from operators import SumOperator
from problog.evaluator import FormulaEvaluatorNSP, FormulaEvaluator
from problog.formula import LogicDAG
from problog.program import PrologString
from problog.sdd_formula import SDD

from wmi_semiring import WmiSemiring

intTime = 0


def solve(model, semiring, operator):
    global intTime
    if semiring.is_dsp():
        t = time.time()
        ev = SDD.create_from(model, label_all=True).to_formula()
        intTime += (time.time() - t)
    else:
        ev = LogicDAG.create_from(model, label_all=True)
    if semiring.is_nsp():
        fe = FormulaEvaluatorNSP(ev, semiring)
    else:
        fe = FormulaEvaluator(ev, semiring)
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
    i = 0
    dict = {}
    for p in set(re.findall(pattern, s)):
        new = "z{}".format(i)
        dict[new] = p
        s = s.replace(p, new)
        i += 1
    Element.dict = dict
    return s


def main(fileName):
    string = open(fileName).read()
    string = transform(string)
    pl = PrologString(string)
    operator = SumOperator()
    result = solve(pl, WmiSemiring(operator.neutral_element), operator)
    for k, v in result.items():
        (formula, integral) = v
        print('%s(%s): %s\n%s' % (operator, k, integral, formula))
        print(formula.key)
    return integral


if __name__ == '__main__':
    t = time.time()
    print("result={}".format(main("../CNF_move")))
    print("time: {}s".format(time.time()-t))
