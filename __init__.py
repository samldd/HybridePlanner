import re


s = """
w(Piecewise((x, (0<x) & (x<1)), (0,True)),1,1)::x1.
w(Piecewise((2-x,(1<x) & (x<2)), ( 0, True )),1,1)::x2.
w(2*Piecewise((x1-y0, (0<x1-y0) & (x1-y0<1)), ( 0, True )),1,1)::x3.
w(2*Piecewise((2-(x2-y1-y2),(1<x2-y1-y2) & (x2-y1-y2<2)), ( 0, True )),1,1)::x4.
"""

sub = "(?:\(.+\))+"
pattern = u"(Piecewise\({}\))".format(sub)

for p in re.findall(pattern, s):
    print p