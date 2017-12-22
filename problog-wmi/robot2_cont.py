from DBN import *
from heuristic import  Action, Effect, ProbEffect, RelaxOperator
# Initial state (robot in 1 and -pushed)
position = Node("p", ["p1", "p2", "p3", "p4"],
                [DRow([], ["1", "0", "0", "0"])])
button = Node("b", ["b"],
              [BRow([], [0])])
init = Layer([position, button], "init")

# Action: move right
move_r_a = Node("mr", ["e1", "e2", "e3", "e4"],
                [CRow([Literal("p", 0)], ["x", "x^3", "1", "0"]),
                 CRow([Literal("p", 1)], ["1", "x^3", "x^2", "0"]),
                 CRow([Literal("p", 2)], ["1", "x^2", "x^3", "0"]),
                 DRow([Literal("p", 3)], ["0", "0", "0", "1"]), ])
move_r_p = Node("p", ["p1", "p2", "p3", "p4"],
                [DRow([Literal("mr", 0)], ["1", "0", "0", "0"]),
                 DRow([Literal("mr", 1)], ["0", "1", "0", "0"]),
                 DRow([Literal("mr", 2)], ["0", "0", "1", "0"]),
                 DRow([Literal("mr", 3)], ["0", "0", "0", "1"])])
move_r_b = Node("b", ["b"],
                [BRow([Literal("b", 0)], ["1"]),
                 BRow([-Literal("b", 0)], ["0"])])
move_r = Layer([move_r_p, move_r_b], "moveRight", move_r_a)

# Action: move left
move_l_a = Node("ml", ["e1", "e2", "e3", "e4"],
                [DRow([Literal("p", 0)], ["0", "0", "0", "1"]),
                 CRow([Literal("p", 1)], ["1", "x^2", "x^3", "x^4"]),
                 CRow([Literal("p", 2)], ["1", "x^3", "x^2", "x^2"]),
                 CRow([Literal("p", 3)], ["x", "x^3", "1", "0"]),])
move_l_p = Node("p", ["p1", "p2", "p3", "p4"],
                [DRow([Literal("ml", 0)], ["0", "0", "0", "1"]),
                 DRow([Literal("ml", 1)], ["0", "0", "1", "0"]),
                 DRow([Literal("ml", 2)], ["0", "1", "0", "0"]),
                 DRow([Literal("ml", 3)], ["1", "0", "0", "0"])])
move_l_b = Node("b", ["b"],
                [BRow([Literal("b", 0)], ["1"]),
                 BRow([-Literal("b", 0)], ["0"])])
move_l = Layer([move_l_p, move_l_b], "move L", move_l_a)

# Action: jump
jump_a = Node("ju", ["e1", "e2", "e3", "e4"],
              [CRow([Literal("p", 0)], ["x", "x", "x", "1"]),
               CRow([Literal("p", 1)], ["x^2", "x^2", "x^2", "x"]),
               CRow([Literal("p", 2)], ["0", "x^2", "x^3", "x^4"]),
               DRow([Literal("p", 3)], ["0", "0", "0", "1"])], )
jump_p = Node("p", ["p1", "p2", "p3", "p4"],
              [DRow([Literal("ju", 0)], ["1", "0", "0", "0"]),
               DRow([Literal("ju", 1)], ["0", "1", "0", "0"]),
               DRow([Literal("ju", 2)], ["0", "0", "1", "0"]),
               DRow([Literal("ju", 3)], ["0", "0", "0", "1"])])
jump_b = Node("b", ["b"],
              [BRow([Literal("b", 0)], ["1"]),
               BRow([-Literal("b", 0)], ["0"])])
jump = Layer([jump_p, jump_b], "jump", jump_a)

# Action: push button
push_p = Node("p", ["p1", "p2", "p3", "p4"],
              [DRow([Literal("p", 0)], ["1", "0", "0", "0"]),
               DRow([Literal("p", 1)], ["0", "1", "0", "0"]),
               DRow([Literal("p", 2)], ["0", "0", "1", "0"]),
               DRow([Literal("p", 3)], ["0", "0", "0", "1"])])
push_b = Node("b", ["b", "p"],
              [BRow([Literal("p", 3)], ["1"]),
               BRow([-Literal("p", 3), Literal("b", 0)], ["1"]),
               BRow([-Literal("p", 3), -Literal("b", 0)], ["0"])])
push = Layer([push_b, push_p], "push")

actions = [ jump, move_r, push]
goal = [Literal("b", 0)]


relax = RelaxOperator()
actions_h = set()

eps1 = ProbEffect("Emr11", 0.09, [], [])
eps2 = ProbEffect("Emr12", 0.71, ["r2"], ["r1"])
eps3 = ProbEffect("Emr13", 0.20, ["r3"], ["r1"])
e1 = Effect(["r1"],[eps1, eps2, eps3])
eps1 = ProbEffect("Emr21", 0.09, ["r1"], ["r2"])
eps2 = ProbEffect("Emr22", 0.34, [], [])
eps3 = ProbEffect("Emr23", 0.57, ["r3"], ["r2"])
e2 = Effect(["r2"],[eps1, eps2, eps3])
eps1 = ProbEffect("Emr31", 0.05, ["r1"], ["r3"])
eps2 = ProbEffect("Emr32", 0.12, ["r2"], ["r3"])
eps3 = ProbEffect("Emr33", 0.83, [], [])
e3 = Effect(["r3"],[eps1, eps2, eps3])
a = Action("moveRight", [e1,e2,e3], [])
actions_h |= {relax.relaxe_action(a)}

eps1 = ProbEffect("Ejp11", 0.10, [], [])
eps2 = ProbEffect("Ejp12", 0.27, ["r2"], ["r1"])
eps3 = ProbEffect("Ejp13", 0.45, ["r3"], ["r1"])
eps4 = ProbEffect("Ejp14", 0.18, ["r4"], ["r1"])
e1 = Effect(["r1"],[eps1, eps2, eps3, eps4])
eps1 = ProbEffect("Ejp21", 0.03, ["r1"], ["r2"])
eps2 = ProbEffect("Ejp22", 0.18, [], [])
eps3 = ProbEffect("Ejp23", 0.50, ["r3"], ["r2"])
eps4 = ProbEffect("Ejp24", 0.29, ["r4"], ["r2"])
e2 = Effect(["r2"],[eps1, eps2, eps3, eps4])
eps1 = ProbEffect("Ejp33", 0.10, [], [])
eps2 = ProbEffect("Ejp34", 0.90, ["r4"], ["r3"])
e3 = Effect(["r3"],[eps1, eps2])
a = Action("jump", [e1,e2,e3], [])
actions_h |= {relax.relaxe_action(a)}

eps1 = ProbEffect("Epush", 1.0, ["b2"], ["b1"])
e1 = Effect(["r3"],[eps1])
a = Action("jump", [e1], [])
actions_h |= {relax.relaxe_action(a)}

proposition_h = ["r1", "r2", "r3", "r4", "b1", "b2"]
init_h = [
    [
         "w(1.0,1,boolean):: r1({0}) .",
         "w(0.0,1,boolean):: r2({0}) .",
         "w(0.0,1,boolean):: r3({0}) .",
         "w(0.0,1,boolean):: r4({0}) .",
         "w(1.0,1,boolean):: b1({0}) .",
         "w(0.0,1,boolean):: b2({0}) .",
     ],
    [
        " r1({0}) ; r2({0}) ; r3({0}) ; r4({0}) ",
        " not r1({0}) ; not r2({0}) ",
        " not r1({0}) ; not r2({0}) ",
        " not r1({0}) ; not r3({0}) ",
        " not r1({0}) ; not r4({0}) ",
        " not r2({0}) ; not r3({0}) ",
        " not r2({0}) ; not r4({0}) ",
        " not r3({0}) ; not r4({0}) ",
        " b1({0}) ; b2({0}) ",
        " not b1({0}) ; not b2({0}) "
    ]
]
goal_h = ["b2"]

if __name__ == "__main__":
    move_r.set_prev_layer(init)
    m2 = move_r.copy()
    m2.set_prev_layer(move_r)
    p, c, _ = m2.convert(0)
    for s in p:
        print s
    for s in c:
        print "(" + s + "),"
    # for s in move_r.convert_goal(goal):
    #     print s
