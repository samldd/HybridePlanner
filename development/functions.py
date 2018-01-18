from Node import Node, CPT


def create_initial_layer():
    x0 = Node("X_0")
    x0_cpt = CPT(x0, ["i1_0", "i2_0", "i3_0", "i4_0"],
                 ["x0=0.0:1.0", "x0=1.0:2.0", "x0=2.0:3.0", "x0=3.0:4.0"])
    x0_cpt.add_row("", ["x0", "2-x0", "0", "0"])
    x0.set_CPT(x0_cpt)
    return {"X_0": x0}


func1 = "2*Piecewise((x{0}-y{0}, (0<x{0}-y{0}) & (x{0}-y{0}<1)), ( 0, True ))"
func2 = "2*Piecewise((2-(x{0}-y{0}),(1<x{0}-y{0}) & (x{0}-y{0}<2)), ( 0, True ))"


def create_layer(t, nodes):
    global func1, func2
    eps = Node("eps_{}".format(t))
    eps_cpt = CPT(eps, ["e1_{}".format(t), "e2_{}".format(t), "e3_{}".format(t)],
                       ["y{}=0.0:1.0".format(t), "y{}=1.0:2.0".format(t), "boolean"])
    eps_cpt.add_row("i1_{}".format(t-1), ["y{}".format(t), "2-y{}".format(t), "0"])
    eps_cpt.add_row("i2_{}".format(t-1), ["1.5*y{}".format(t), "1-0.5*y{}".format(t), "0"])
    eps_cpt.add_row("i3_{}".format(t-1), ["0", "0", "1"])
    eps_cpt.add_row("i4_{}".format(t-1), ["0", "0", "1"])
    eps.set_CPT(eps_cpt)
    eps.add_parent(nodes["X_{}".format(t-1)])
    nodes["eps_{}".format(t)] = eps

    x = Node("X_{}".format(t))

    x_cpt = CPT(x, ["i1_{}".format(t), "i2_{}".format(t), "i3_{}".format(t), "i4_{}".format(t)],
                    ["x{}=0.0:1.0".format(t), "x{}=1.0:2.0".format(t), "x{}=2.0:3.0".format(t), "x{}=3.0:4.0".format(t)])
    x_cpt.add_row("i1_0,e1_{1}".format(t-1,t), [func1.format(*range(1,t+1))]*4)
    x_cpt.add_row("i1_0,e2_{1}".format(t-1,t), [func1.format(*range(1,t+1))]*4)
    x_cpt.add_row("i2_0,e1_{1}".format(t-1,t), [func2.format(*range(1,t+1))]*4)
    x_cpt.add_row("i2_0,e2_{1}".format(t-1,t), [func2.format(*range(1,t+1))]*4)
    func1 = func1.replace("x{%d}" %(t-1), "x{%d}-y{%d}" %(t,t))
    func2 = func2.replace("x{%d}" %(t-1), "x{%d}-y{%d}" %(t,t))
    x_cpt.add_row("i3_{0},e3_{1}".format(t-1,t), ["0", "0", "1", "0"])
    x_cpt.add_row("i4_{0},e3_{1}".format(t-1,t), ["0", "0", "0", "1"])
    x.set_CPT(x_cpt)
    x.add_parent(nodes["eps_{}".format(t)])
    x.add_parent(nodes["X_{}".format(t-1)])
    nodes["X_{}".format(t)] = x
    return nodes