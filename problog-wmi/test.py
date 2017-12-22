import sympy as sp
from skmonaco import mcquad
import time

x0, y1, x1, y2,x2 = sp.symbols('x0 y1 x1 y2 x2')
Fx0 = x0
Fy1 = y1
Fx1 = sp.Piecewise((2*(x1-y1), sp.And(0<x1-y1, x1-y1<1)), ( 0, True ))
Fy2 = y2
Fx2 = sp.Piecewise((2*(x2-y1-y2), sp.And(0<x2-y1-y2, x2-y1-y2<1)), ( 0, True ))

integrand = Fx0*Fy1*Fx1*Fy2*Fx2
func = lambda s1, s2, s3, s4, s5: integrand.subs([(x0,s1),(y1,s2),(x1,s3),(y2,s4),(x2,s5)])
lb = [0.0,0.0,0.0,0.0,1.0]
ub = [1.0,1.0,1.0,1.0,2.0]
t = time.time()
print mcquad(lambda x: float(apply(func,x)),100,lb,ub)
print (time.time()-t)