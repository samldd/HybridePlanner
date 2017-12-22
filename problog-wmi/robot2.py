from ActionNode import *

# Initial state (robot in 1 and -pushed)
position = DNode("position",[],[],
                 ["i1","i2","i3","i4"],
                 [[1,0,0,0]])
button = DNode("button", [], [],
              ["p"],
              [[0]])
init = Layer([position, button])

# Action: move right
move_r_a = CNode("move_r","position",
                 [(Literal("position",0),),
                  (Literal("position",1),),
                  (-Literal("position",0),-Literal("position",1),)],
                 ["e1","e2","e3"],
               [[0.85,0.15,0.00],
                [0.10,0.90,0.00],
                [0.00,0.00,1.00]])
move_r_p = DNode("position",["position","move_r"],
                 [(Literal("move_r",0),),
                  (Literal("move_r",1),),
                  (Literal("move_r",2),Literal("position",0),),
                  (Literal("move_r",2),Literal("position",1),),
                  (Literal("move_r",2),Literal("position",2),),
                  (Literal("move_r",2),Literal("position",3),)],
                 ["i1","i2","i3","i4"],
                 [[0,1,0,0],
                  [0,0,1,0],
                  [1, 0, 0, 0],
                  [0, 1, 0, 0],
                  [0, 0, 1, 0],
                  [0, 0, 0, 1],])
move_r_b = DNode("button", ["button"],
                 [(Literal("button",0),),
                  (-Literal("button",0),)],
                 ["p"],
                 [[1],
                  [0]])
move_r = Layer([move_r_p, move_r_b],move_r_a)

# Action: jump
jump_a = CNode("jump","position",
               [ (Literal("position",0),),
                 (Literal("position",1),),
                (-Literal("position",0),-Literal("position",1),)],
               ["e1","e2","e3"],
               [[0.38,0.60,0.02],
                [0.20,0.60,0.20],
                [0.00,0.00,1.00],])
jump_p = DNode("position",["position","jump"],
               [(Literal("jump",0),),
                (Literal("jump",1),),
                (Literal("jump",2),),
                (-Literal("jump", 0), -Literal("jump", 1), -Literal("jump", 2), Literal("position", 0),),
                (-Literal("jump", 0), -Literal("jump", 1), -Literal("jump", 2), Literal("position", 1),),
                (-Literal("jump", 0), -Literal("jump", 1), -Literal("jump", 2), Literal("position", 2),),
                (-Literal("jump", 0), -Literal("jump", 1), -Literal("jump", 2), Literal("position", 3),)],
                 ["i1","i2","i3","i4"],
                 [[0,1,0,0],
                  [0,0,1,0],
                  [0,0,0,1],
                  [1, 0, 0, 0],
                  [0, 1, 0, 0],
                  [0, 0, 1, 0],
                  [0, 0, 0, 1]])
jump_b = DNode("button", ["button"],
               [(Literal("button",0),),
                (-Literal("button",0),)],
               ["p"],
               [[1],
                [0]])
jump = Layer([jump_p, jump_b],jump_a)

#Action: push button
push_p = DNode("position",["position"],
               [(Literal("position",0),),
                (Literal("position",1),),
                (Literal("position",2),),
                (Literal("position",3),),],
               ["i1", "i2", "i3", "i4"],
               [[1,0,0,0],
                [0,1,0,0],
                [0,0,1,0],
                [0,0,0,1]])
push_b = DNode("button",["button","position"],
               [ (Literal("position",3),),
                (-Literal("position",3),Literal("button",0),),
                (-Literal("position",3),-Literal("button",0),),],
               ["p"],
               [[1],
                [1],
                [0]])
push = Layer([push_b,push_p])

# Action: move left
move_l_a = CNode("move_l","position",
                 [(Literal("position",3),),
                  (Literal("position",2),),
                  (Literal("position",1),),
                 (-Literal("position",1),-Literal("position",2),-Literal("position",3),)],
                 ["e1","e2","e3","e4"],
               [[0.00,0.20,0.55,0.25],
                [0.20,0.70,0.10,0.00],
                [1.00,0.00,0.00,0.00],
                [0.00,0.00,0.00,1.00]])
move_l_p = DNode("position",["position","move_r"],
                 [(Literal("move_l",0),),
                  (Literal("move_l",1),),
                  (Literal("move_l",2),),
                  (Literal("move_l",3),Literal("position",0),),
                  (Literal("move_l",3),Literal("position",1),),
                  (Literal("move_l",3),Literal("position",2),),
                  (Literal("move_l",3),Literal("position",3),)],
                 ["i1","i2","i3","i4"],
                 [[1,0,0,0],
                  [0,1,0,0],
                  [0,0,1,0],
                  [1, 0, 0, 0],
                  [0, 1, 0, 0],
                  [0, 0, 1, 0],
                  [0, 0, 0, 1],])
move_l_b = DNode("button", ["button"],
                 [(Literal("button",0),),
                  (-Literal("button",0),)],
                 ["p"],
                 [[1],
                  [0]])
move_l = Layer([move_l_p, move_l_b],move_l_a)

actions = [jump, push, move_l]

goal = [Literal("position",0),Literal("button",0)]

if __name__ == "__main__":
    a1 = jump.copy()
    a2 = jump.copy()
    a3 = push.copy()
    a4 = push.copy()

    a4.set_prev_layer(a3)
    a3.set_prev_layer(a2)
    a2.set_prev_layer(a1)
    a1.set_prev_layer(init)

    (propositions, clauses) = init.convert()
    # (propositions, clauses) = a1.convert()
    # (propositions, clauses) = a2.convert()
    # (propositions, clauses) = a3.convert()
    # (propositions, clauses) = a4.convert()