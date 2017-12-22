from __future__ import print_function

import time

from operators import SumOperator
from problog.evaluator import FormulaEvaluatorNSP, FormulaEvaluator
from problog.formula import LogicDAG
from problog.program import PrologString, PrologFile
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
    a = []
    pl = PrologFile("test_node")
    operator = SumOperator()
    t = time.time()
    # for _ in range(0,10):
    result = solve(pl, WmiSemiring(operator.neutral_element), operator)
    print("time: {}s".format(time.time()-t))
    for k, v in result.items():
        (formula, integral) = v
        print(formula)
        print(integral)
    #     a += [integral]
    # a = map(lambda x: float(x), a)
    # print(np.mean(a))
    # print(np.std(a))


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
