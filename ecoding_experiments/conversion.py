import re

stateProp = re.compile("w\(1,1,boolean\)::(?P<name>\w*)\.")
chanceProp = re.compile("w\((?P<pos>[0-9]*\.?[0-9]*),[0-9]*\.?[0-9]*,boolean\)::(?P<name>\w*)\.")
clause = re.compile("not\s\w+|\w+")

variables = []
clauses = []

def convert_problog(input):
    global variables, clauses
    f = open(input)
    for line in f.readlines():
        res = stateProp.findall(line)
        if res:
            variables.append("w {} -1\n".format(res[0][1:]))
            continue
        res = chanceProp.findall(line)
        if res:
            variables.append("w {0} {1}\n".format(res[0][1][1:], res[0][0]))
            continue
        if line == "f:-\n" or line == "query(f).":
            continue
        res = clause.findall(line)
        if res:
            s = ""
            for c in res:
                if c[0:3] == "not":
                    s += "-" + c[5:] + " "
                else:
                    s += c[1:] + " "
            s += "0\n"
            clauses.append(s)
    f.close()
    f = open("darts_5.cachet", "w")
    f.write("p {0} {1}\n".format(len(variables), len(clauses)))
    for v in variables:
        f.write(v)
    for c in clauses:
        f.write(c)
    f.close()

def add(clauses, num):
    for i in range(16,0,-1):
        clauses = clauses.replace("x"+str(i)+" ","x"+str(i+num))
    print clauses
def add2(clauses, num):
    for i in range(16,8,-1):
        clauses = clauses.replace("x"+str(i),"x"+str(i+num))
    print clauses



if __name__ == "__main__":
    convert_problog("domains/darts_5.probLog")



pred = """
( x9 ; x10 ; x11 ),
( not x9 ; not x10 ),
( not x9 ; not x11 ),
( not x10 ; not x11 ),
( not x12 ; x9 ),
( x12 ; not x13; x10 ),
( x12 ; x13; x11 ),
( not x9 ; x14 ),
( not x10 ; x15 ),
( not x11 ; x16 ),
( not x6 ; x14 ),
( not x7 ; x15 ),
( not x8 ; x16 ),
( x6 ; x9 ; not x14 ),
( x7 ; x10 ; not x15 ),
( x8 ; x11 ; not x16 ),
"""
pred2 = """
w(1,1,boolean)::x9.
w(1,1,boolean)::x10.
w(1,1,boolean)::x11.
w(0.560000,0.440000,boolean)::x12.
w(0.750000,0.250000,boolean)::x13.
w(1,1,boolean)::x14.
w(1,1,boolean)::x15.
w(1,1,boolean)::x16.
"""

