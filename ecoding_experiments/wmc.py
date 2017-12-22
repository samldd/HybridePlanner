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
        # print(a)
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
    t = time.time()
    if semiring.is_dsp():
        ev = SDD.create_from(model, label_all=True).to_formula()
        print ev

        print "SDD time: {}".format(time.time() - t)
        exit(0)
    else:
        ev = LogicDAG.create_from(model, label_all=True)
    if semiring.is_nsp():
        fe = FormulaEvaluatorNSP(ev, semiring)
    else:
        fe = FormulaEvaluator(ev, semiring)

    weights = ev.extract_weights(semiring=semiring)
    # print weights
    fe.set_weights(weights)

    result = {}
    [(n, q)] = ev.queries()
    p = fe.evaluate(q)
    result[n] = p
    return result

def wmc(file):
    pl = PrologFile(file)
    result = solve(pl, CachetSemiring())
    return result.items()[0][1]

def argparser():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    return parser

if __name__ == "__main__":
    import sys, time
    # if len(sys.argv) < 2:
    #     exit(1);
    t = time.time()
    # print wmc(sys.argv[1])
    for _ in range(0,1):
        wmc("domains/darts_5.probLog")
    print time.time()-t