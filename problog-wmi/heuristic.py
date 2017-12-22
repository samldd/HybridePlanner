import re
from sys import maxint
from wmi import main
import time

# Global variables
propositions = None
goal = None
goal_p = None
m = None
init = None
phi = None
actions = None
NOOPS = None
T = 0
G = {}
weights = {}
imp = set()
A = None
P = None
uP = None
relaxedSeq = []

class Fact(object):

    def __init__(self, name, weight, time, chance_node=False):
        self.name = name
        self.t = time
        self.weight = weight
        self.chanceNode = chance_node

    def __repr__(self):
        return "{0}({1})".format(self.name, self.t)

    def __hash__(self):
        return hash(self.name) + hash(self.t)

    def __eq__(self, other):
        if not type(self) == type(other):
            return False
        return self.name == other.name and self.t == other.t


class Action:

    def __init__(self, name, effect=None, precondition=None):
        self.name = name
        self.time = None
        self.effect = effect
        self.precondition = precondition

    def get_time(self):
        if not self.time:
            Exception("No time set for " + str(self) + " yet.")
        else:
            return self.time

    def __str__(self):
        # s = "@@Action: " + self.name + "\n"
        # s += "@@precondition: " + str(self.precondition) + "\n"
        # for e in self.effect:
        #     s += str(e)
        # return s
        if self.time:
            return self.name + "(" + str(self.time) + ")"
        return self.name

    def __repr__(self):
        if self.time >= 0:
            return self.name + "(" + str(self.time) + ")"
        return self.name


class Effect:

    def __init__(self, condition, effect):
        self.condition = condition
        self.effect = effect

    def get_cond(self, t):
        for cond in self.condition:
            return Fact(cond,1,t)
        return None

    def sat_cond(self, cond):
        return cond in self.condition

    def __repr__(self):
        s = "@condition: {0},\n@effect: ".format(self.condition)
        for e in self.effect:
            s += "{}\n\t\t ".format(e)
        return s

    def __str__(self):
        s =  "@condition: {0}\n@effect: ".format(self.condition)
        for e in self.effect:
            s += "{}\n\t\t ".format(e)
        return s


class ProbEffect:

    def __init__(self, name, probability, add, delete):
        self.name = name
        self.probability = probability
        self.add = add
        self.delete = delete

    def as_fact(self,t):
        return Fact(self.name, self.probability, t)

    def __repr__(self):
        return self.name + ":({0}, {1}, {2})".format(self.probability, self.add, self.delete)


class RelaxOperator:
    """
    The relax operator, relaxes an action on the following way:
        1. Remove the delete list
        2. Convert actions to their 2-projection (Keep only one of the conditions)
    """

    def __init__(self):
        pass

    def relaxe_action(self, action):
        for effect in action.effect:
            try:
                condition = effect.condition.pop()
                effect.condition = [condition]
            except Exception:
                pass
            for peffect in effect.effect:
                peffect.delete = []
        return action



## Initialization


def initialize(propositions1, goal1, init1, actions1):
    global propositions, goal, init, actions, NOOPS
    propositions = propositions1
    goal = goal1
    init = init1
    actions = actions1
    NOOPS = set()
    for p in propositions:
        eps1 = ProbEffect("E"+p, 1.0, [p], [])
        e = Effect([p], [eps1])
        a = Action("noop_"+p, [e], [])
        NOOPS |= {a}


## Methods for PRPG construction


def get_weight(wpt, p):
    try:
        return weights[wpt][p]
    except KeyError:
        return 0


def set_weight(wpt, pt, val):
    global weights, propositions
    if wpt not in weights:
        weights[wpt] = {}
    weights[wpt][pt] = val


def get_imp_u(p, imp1):
    """
    :param p: The proposition for which the reachable implication graph has to build
    :param imp1: The original implication graph
    :return: A new implication graph which has p as its endpoint
    """
    intermediate = result = {(a, b) for (a, b) in imp1 if b == p}
    while True:
        tmp = set()
        for (a, b) in intermediate:
            tmp = set.union(tmp, {(c, d) for (c, d) in imp1 if d == a})
        intermediate = tmp
        result = result.union(tmp)
        if not tmp:
            break
    return result


def get_imp_u2(p, imp):
    """
    :param p: a proposition
    :param imp: the original implication graph
    :return: All propositions which are in the reachable implication graph of p
    """
    result = {p}
    while True:
        tmp = set()
        for p in result:
            tmp |= {c for (c, d) in imp if d == p}
        if not tmp - result:
            return result
        result = result.union(tmp)


debug_wil = False


def build_w_impleafs(p):
    global A
    if debug_wil:
        print "==" + str(p) + "=="
    set_weight(p, p, 1)  # w_p(t)(p(t)) = 1
    imp_u = get_imp_u2(p, imp)
    for t1 in range(p.t - 1, m - 1, -1):
        for chance_node in {n for n in imp_u if n.chanceNode and n.t == t1}:
            alpha = 1
            for r in [Fact(b.name, 1, t1 + 1) for (a, b) in get_imp_u(p, imp) if a == chance_node]:
                alpha *= (1 - get_weight(p, r))
            if debug_wil:
                print "--chncnode--" + str(chance_node) + "----"
                print "w_" + str(p) + "(" + str(chance_node) + ") = " + str(chance_node.weight * (1 - alpha))
            set_weight(p, chance_node, chance_node.weight * (1 - alpha))
        for fact_node in [a for a in imp_u if not a.chanceNode and a.t == t1]:  # for all fact nodes q(t1)
            alpha = 1
            if debug_wil:
                print "--fctnode--" + str(fact_node) + "----"
            for cond_e in [cond_e for a in A[t1] for cond_e in a.effect if cond_e.sat_cond(fact_node.name)]:
                if debug_wil:
                    print "conde::" + str(cond_e) + "----" + str(sum([get_weight(p, Fact(prob_e.name, 1, t1)) for prob_e in cond_e.effect if
                         Fact(prob_e.name, prob_e.probability, t1) in imp_u]))
                alpha *= (1 - sum([get_weight(p, Fact(prob_e.name, 1, t1)) for prob_e in cond_e.effect if
                                   Fact(prob_e.name, prob_e.probability, t1) in imp_u]))
            if debug_wil:
                print "w_" + str(p) + "(" + str(fact_node) + ") = " + str(1 - alpha)
            set_weight(p, fact_node, 1 - alpha)  # w_p(t)(q(t1)) = 1 - alpha
        if debug_wil:
            print "\n"
    if debug_wil:
        print "\n"


def help_leafs(p, imp1):
    for (_, c) in imp1:  # If there is something which points to p
        if p == c:
            return set()
    return {p}


def get_leafs(imp1):
    leafs = set()
    for (a, _) in imp1:
        leafs |= help_leafs(a, imp1)
    return leafs


def support(p):
    return {l for l in get_leafs(get_imp_u(p, imp)) if get_weight(p, l) == l.weight}


def implies(formula, implication):
    s = ""
    count = 1
    state_prop = re.compile("w\((?:(?:[0-9]*\.[0-9]*)|1),1,boolean\)::(.*)\.")
    var_map = {}
    for p in formula[0]:
        s += p + "\n"
    for p in state_prop.findall(s):
        var_map[p] = " x{} ".format(count)
        count += 1
    s += "\nf:-\n"
    for i in range(0, len(formula[1])):
        s += "\t(" + formula[1][i] + "),\n"
    s += "\t(" + implication + " ).\n\n"
    s += "query(f)."
    for v in var_map:
        s = s.replace(v, var_map[v])
    try:
        return main(s) == 1
    except TypeError:
        return False


debug_timestep = False


def build_time_step(t):
    global imp, P, uP, weights, init
    P[t + 1] = set()
    for p in P[t]:
        P[t + 1] |= {Fact(p.name, p.weight, p.t + 1)}
    uP[t + 1] = set()
    for cond_e in [cond_e for a in A[t] for cond_e in a.effect if cond_e.get_cond(t) in set.union(P[t], uP[t]) or cond_e.get_cond(t) == None]:
        facts = []
        for prob_e in cond_e.effect:
            uP[t + 1] = uP[t + 1].union({Fact(add, 1, t + 1) for add in prob_e.add}-P[t+1])
            eps = Fact(prob_e.name, prob_e.probability, t, True)  # new fact eps(t), with w(eps(t)) = Pr(eps)
            for add in prob_e.add:
                set_weight(Fact(add, 1, t), eps, prob_e.probability)
            facts.append(eps)
            # Imp = Imp U {(eps(t),p(t+1))|p in add(eps)})
            imp = imp.union({(eps, p) for p in uP[t + 1] if p.name in prob_e.add})
            if cond_e.get_cond(t) in uP[t] and len(prob_e.add):
                imp = imp.union({(cond_e.get_cond(t), eps)})
        if not cond_e.get_cond(t) in uP[t]:
            clauses = []
            prop = []
            clause1 = ""
            for i in range(0, len(facts)):
                clause1 += "; {} ".format(str(facts[i]))
                prop.append("w({0},1,boolean):: {1} .".format(facts[i].weight, facts[i]))
                for j in range(i + 1, len(facts)):
                    clauses.append("not {0} ; not {1} ".format(facts[i], facts[j]))
            clause1 = clause1[1:]
            clauses.append(clause1)
            phi[0] += prop
            phi[1] += clauses
    for p in uP[t + 1]:
        build_w_impleafs(p)
        if debug_timestep:
            print "====" + str(p) + "===="
            for l in get_leafs(get_imp_u(p, imp)):
                print str(l) + " : " + str(get_weight(p, l)) + " : " + str(l.weight)
            print "==> " + str(support(p))
        clause = ""
        for l in support(p):
            clause += "; {} ".format(l)
        clause = clause[1:]
        if False: #implies(phi, clause):
            P[t + 1] |= {p}
    if debug_timestep:
        print "\n"
    uP[t + 1] = uP[t + 1] - P[t + 1]


debug_P = False


def get_P(t, G):
    goals = {Fact(g, 1, t) for g in G}
    if debug_P:
        print "\n=== get P ==="
        print goals - P[t]
    if not goals.issubset(P[t] | uP[t]):
        return 0
    if goals.issubset(P[t]):
        return 1
    propositions = []
    clauses = []
    for g in goals - P[t]:
        conj = ""
        for l in get_leafs(get_imp_u(g,imp)):
            conj += "; {0} ".format(l)
        for l in get_leafs(get_imp_u(g,imp))&uP[m] :
            # Introduce a chance proposition <l_g> with weight w_g(t)(l)
            w = get_weight(g,l)
            propositions.append("w({0},{1},boolean):: {2}{3} .".format(w,1-w,g,l)) # TODO: no negative info?!
            clauses.append("not {0} ; {1}{0} ".format(l,g))
        clauses.append(conj[1:])
    propositions += phi[0]
    clauses += phi[1]
    s = ""
    count = 1
    stateProp = re.compile("w\((?:(?:[0-9]*\.[0-9]*)|1|0),(?:(?:[0-9]*\.[0-9]*)|1),boolean\)::(.*)\.")
    map = {}
    for p in propositions:
        s += p + "\n"
    for p in stateProp.findall(s):
        map[p] = " x{} ".format(count)
        count += 1
    s += "\nf:-\n"
    for i in range(0, len(clauses)-1):
        s += "\t(" + clauses[i] + "),\n"
    s += "\t(" + clauses[-1] + ").\n\n"
    s += "query(f)."
    if debug_P:
        print "---------------------"
        print s
    for v in map:
        s = s.replace(v, map[v])
    try:
        res = main(s)
    except Exception:
        print s
        exit()
    return res


def build_PRPG(sequence, G, theta):
    global A, P, uP, debug_timestep, debug_wil, m, actions, NOOPS
    for t in range(m, 0):
        A[t] = [a for a in actions if a.name == sequence[t]] + [p for p in NOOPS]
        build_time_step(t)
    t = 0
    while get_P(t, G) < theta:
        A[t] = [noop for noop in NOOPS if noop.effect[0].get_cond(t) in uP[t]] + [a for a in actions]
        build_time_step(t)
        if all([Fact(p.name,1,t-1) in P[t] for p in P[t+1]]) \
            and all([Fact(p.name,1,t-1) in uP[t] for p in uP[t+1]]) \
            and get_P(t+1,G) == get_P(t,G) \
            and all([set.intersection(uP[-m], support(p)) == set.intersection(uP[-m], support(Fact(p.name,1,p.t-1))) for p in uP[t + 1]]): #and get_P(t+1, G) == get_P(t, G):
            return False
        t += 1
    return True


## Methods for plan extraction


def sub_goal(gp_t):
    global P
    for p in gp_t:
        t0 = min([t for t in P if Fact(p.name, 1, t) in P[t]])
        if t0 >= 1:
            if t0 not in G:
                G[t0] = set()
            G[t0] = {Fact(p.name, 1, t0)}


def extract_subplan(imp1):
    global actions
    for (eps, p) in [(eps, p) for (eps, p) in imp1 if eps.chanceNode and eps.t >= 0]:
        for a in actions:
            cond = [c_eff for c_eff in a.effect for p_eff in c_eff.effect if eps.name == p_eff.name]
            if cond :
                a1 = Action(str(a))
                a1.time = eps.t
                relaxedSeq.append(a1)
                sub_goal({cond[0].get_cond(eps.t)} & P[eps.t])


def reduce_implication_graph(imp, theta, sequence):
    imp1 = set()
    for g in goal_p - P[T]:
        imp1 |= get_imp_u(g, imp)

    return imp1
    for action in [action for a_n in sequence for action in actions if action.name == a_n]: # For all actions in the initial sequence
        action = [p_eff.name for c_eff in action.effect for p_eff in c_eff.effect]
        impli = [(eps,p) for (eps,p) in imp1 if eps.t >= 0 and (eps.name in action or p.name in action)]
        for t in {eps.t for (eps,_) in impli}:
            imp2 = imp1 - set()
            for (eps,p) in {(eps,p) for (eps,p) in impli if eps.t == t}:
                imp2.remove((eps,p))
            propositions = []
            clauses = []
            for g in goal_p - P[T]: # TODO: klopt volgens mij nog niet, moet gewoon voor goal-P[T], maar de gewichten moeten gewoon aangepast worden
                conj = ""
                for l in get_leafs(get_imp_u(g,imp2)):
                    propositions.append("w({0},1,boolean):: {1}{2} .".format(get_weight(g,l),l,g))
                    if l in uP[-1]:
                        clauses.append(" not {0} ; {1}{2} ".format(l, l, g))
                    conj += "; {} ".format(l)
                clauses.append(conj[1:])
            propositions += phi[0]
            clauses += phi[1]
            s = ""
            count = 1
            stateProp = re.compile("w\((?:(?:[0-9]*\.[0-9]*)|1),(?:(?:[0-9]*\.[0-9]*)|1),boolean\)::(\s.+\s)\.")
            map = {}
            for p in propositions:
                s += p + "\n"
            for p in stateProp.findall(s):
                map[p] = " x{} ".format(count)
                count += 1
            s += "\nf:-\n"
            for i in range(0, len(clauses) - 1):
                s += "\t(" + clauses[i] + "),\n"
            s += "\t(" + clauses[-1] + ").\n\n"
            s += "query(f)."
            for v in map:
                s = s.replace(v, map[v])
            print main(s)
            if main(s) >= theta:
                imp1 = imp2
            else:
                break
    return imp1


def construct_support_graph(gt):
    imp1 = set()
    open1 = support(gt)
    while open1:
        p = open1.pop()
        at = [cond_e for a in A[p.t] for cond_e in a.effect if cond_e.sat_cond(p.name)]
        for a in at:
            for prob_e in a.effect:
                e = prob_e.as_fact(p.t)
                if not ((p, e) in get_imp_u(gt, imp) and get_weight(gt, e) == e.weight):
                    at.remove(a)
                    break
        if not at:
            continue
        for eps in at[0].effect:
            q = None
            for add in eps.add:
                if get_weight(gt, Fact(add, 1, p.t + 1)) == 1:
                    q = Fact(add, 1, p.t + 1)
                    break
            imp1 |= {(p, Fact(eps.name, eps.probability, p.t, True)), (Fact(eps.name, eps.probability, p.t, True), q)}
            open1 |= {q}
    return imp1


def extract_PRPlan(imp, theta, sequence):
    imp1 = reduce_implication_graph(imp, theta, sequence)
    extract_subplan(imp1)
    for t in G:
        sub_goal(G[t] & P[T])
    for t in range(T, 0, -1):
        if t not in G:
            continue
        for g in G[t]:
            for a in [a for a in A[t - 1] for cond_e in a.effect for prob_e in cond_e.effect if
                      cond_e.get_cond(t - 1)in P[t - 1] and g in prob_e.add]:
                name = ""
                for a1 in actions:
                    if a1.name == a:
                        break
                relaxedSeq.append(name)
                sub_goal({Fact(a[0], 1, t)})
                break
            else:
                imp_gt = construct_support_graph(g)
                extract_subplan(imp_gt)


## Calculate heuristic value


def get_heuristic_value(sequence, theta, debug=False):
    global m, P, uP, propositions, phi, goal, relaxedSeq, weights, A, T, G, goal_p
    relaxedSeq = []
    m = -len(sequence)
    weights = {}
    A = {}
    G = {}
    phi = [[], []]
    phi[0] = [a.format(m) for a in init[0]]
    phi[1] = [a.format(m) for a in init[1]]
    P = {m: set()}
    uP = {m: {Fact(p, 1, m) for p in propositions}}
    reachable = build_PRPG(sequence, goal, theta)
    if debug:
        print_PRPG_debug()
    if not reachable:
        return maxint
    T = max(uP)
    goal_p = {Fact(g, 1, T) for g in goal}
    extract_PRPlan(imp, theta, sequence)
    # print relaxedSeq
    return len(relaxedSeq)


def print_PRPG_debug():
    global P, uP, imp, A, weights
    print "\n\n==== PRPG END ===="
    print "---- P ----"
    for t in P:
        print str(t) + " : " + str(P[t])
    print "---- unknown P ----"
    for t in uP:
        print str(t) + " : " + str(uP[t])
    print "---- Imp ----"
    for t in range(m, 3):
        print str(t) + " : " + str({(a, b) for (a, b) in imp if a.t == t})
    print "---- Actions ----"
    for t in A:
        print str(t) + " : " + str(A[t])
    print "---- Weight table ----"
    for t in weights:
        print str(t) + " : " + str(weights[t])
    print "\n"


if __name__ == "__main__":
    import time

    tdart = time.time()
    # Need to define an initial state formula
    init = [
        ["w(0.9,1,boolean):: r1({0}) .",
         "w(0.1,1,boolean):: r2({0}) .",
         "w(1,1,boolean):: b1({0}) .",
         "w(1,1,boolean):: b2({0}) .",
         "w(0.7,1,boolean):: b1r1({0}) .",
         "w(0.3,1,boolean):: b2r1({0}) .",
         "w(0.2,1,boolean):: b1r2({0}) .",
         "w(0.8,1,boolean):: b2r2({0}) ."],
        [" r1({0}) ; r2({0}) ",
         " b1({0}) ; b2({0}) ",
         "not r1({0}) ; not r2({0}) ",
         "not b1({0}) ; not b2({0}) ",
         "not r1({0}) ; not b1r1({0}) ; b1({0}) ",
         "not r1({0}) ; not b2r1({0}) ; b2({0}) ",
         " b1r1({0}) ; b2r1({0}) ",
         "not r2({0}) ; not b1r2({0}) ; b1({0}) ",
         "not r2({0}) ; not b2r2({0}) ; b2({0}) ",
         " b1r2({0}) ; b2r2({0}) "]
    ]

    # Define a proposition for each value of a variable
    propositions = ["r1", "r2", "b1", "b2"]

    # Define the goal
    goal = {"r1", "b2"}

    relax = RelaxOperator()
    actions = set()

    # Move Block Right
    eps1 = ProbEffect("Embr1", 0.7, ["r2", "b2"], ["r1", "b1"])
    eps2 = ProbEffect("Embr2", 0.2, ["r2"], ["r1"])
    eps3 = ProbEffect("Embr3", 0.1, [], [])
    e = Effect(["b1", "r1"], [eps1, eps2, eps3])
    a = Action("moveBlockRight", [e], [])
    actions |= {relax.relaxe_action(a)}

    # Move Left
    eps1 = ProbEffect("Eml", 1.0, ["r1"], ["r2"])
    e = Effect(["r2"], [eps1])
    a = Action("MoveLeft", [e], [])
    actions |= {relax.relaxe_action(a)}

    # initialize(propositions, goal, init, actions)
    # print get_heuristic_value(["moveBlockRight"])
    print "time for darts heuristic: {}".format(time.time() - tdart)

    tdart = time.time()
    ## DARTS
    init = [[
        "w(0.0,1,boolean):: i1({0}) .",
        "w(0.0,1,boolean):: i2({0}) .",
        "w(0.0,1,boolean):: i3({0}) .",
    ],[]]
    relax = RelaxOperator()
    actions = set()

    propositions = ["i1", "i2", "i3"]
    goal = ["i3"]
    eps1 = ProbEffect("Et1", 0.11, ["i1"], [])
    eps2 = ProbEffect("Et2", 0.33, ["i2"], [])
    eps3 = ProbEffect("Et3", 0.56, ["i3"], [])
    e = Effect([],[eps1, eps2, eps3])
    a = Action("throw", [e], [])
    actions |= {relax.relaxe_action(a)}

    eps1 = ProbEffect("EDummy", 1.0, [], [])
    e = Effect([],[eps1])
    a = Action("dummy", [e], [])
    actions |= {relax.relaxe_action(a)}

    initialize(propositions, goal, init, actions)
    print get_heuristic_value(["throw"])
    print "time for darts heuristic: {}".format(time.time()-tdart)
