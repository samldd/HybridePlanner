import re

from problog.evaluator import Semiring, FormulaEvaluatorNSP, FormulaEvaluator
from problog.formula import LogicDAG
from problog.program import PrologFile
from problog.sdd_formula import SDD


class CachetSemiring(Semiring):
    def __init__(self):
        Semiring.__init__(self)

    def zero(self):
        return 0

    def one(self):
        return 1

    def plus(self, a, b):
        return a + b

    def times(self, a, b):
        return a * b

    def pos_value(self, a, key=None):
        print(a)
        m = re.search(r"w\((.*),.*,.*\)", str(a))
        return float(m.group(1))

    def neg_value(self, a, key=None):
        m = re.search(r"w\(.*,(.*),.*\)", str(a))
        return float(m.group(1))

    def is_dsp(self):
            return True

    def is_nsp(self):
        return True


def solve(model, semiring):
    if semiring.is_dsp():
        ev = SDD.create_from(model, label_all=True).to_formula()
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
        result[n] = p
    return result


def main(file):
    pl = PrologFile(file)

    result = solve(pl, CachetSemiring())

    for k, v in result.items():
        print ('(%s): %s' % (k, v))


def argparser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    return parser


if __name__ == '__main__':
    main(**vars(argparser().parse_args()))

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
