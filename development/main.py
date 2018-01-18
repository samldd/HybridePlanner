from functions import create_initial_layer, create_layer
from WMI.wmi_mc import main
import time


tmax = 4
# Initialize network
bayesian_network = create_initial_layer()
for t in range(1,tmax+1):
    create_layer(t, bayesian_network)


def print_list(l):
    for e in l:
        print e


goal = "i1_4" # bayesian_network["X_{}".format(tmax)]
literals = []
clauses = []
for k in bayesian_network:
    bayesian_network[k].convert(literals, clauses)

# print_list(literals)
# print_list(clauses)

string = ""
for l in literals:
    string += l + "\n"
string += "f:-"
for c in clauses:
    string += c + "\n"
string += goal + ". \n"
string += "query(f)."

t = time.time()
print("result={}".format(main(string)))
print("time: {}s".format(time.time()-t))