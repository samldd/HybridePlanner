import re


s = """
w(Piecewise((x, (0<x) & (x<1)), (0,True)),1,1)::x1.
w(Piecewise((x, (0<x) & (x<1)), (0,True)),1,1)::x1.
w(Piecewise((x, (0<x) & (x<1)), (0,True)),1,1)::x1.
w(Piecewise((x, (0<x) & (x<1)), (0,True)),1,1)::x1.
"""

sub = "(?:\(.+\))+"
pattern = u"(Piecewise\({}\))".format(sub)

i = 0
dict = {}

print set(re.findall(pattern, s))

for p in re.findall(pattern, s):
    new = "x{}".format(i)
    dict[new] = p
    s = s.replace(p, new)
    i += 1

print s