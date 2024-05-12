from Crypto.Util.number import *
from sympy.polys.galoistools import gf_crt
from sympy.polys.domains import ZZ
import gmpy2
import random
'''
def solve_discrete_log(p, g, A, B):
    F = GF(p)
    g, A = F(g), F(A)
    a = discrete_log(A,g)
    return pow(B, int(a), p)
'''
def Pohlig_Hellman(g, h, p):
    p_1 = p - 1
    d, factors = 2, []
    while p_1!=1:
        while (p_1 % d) == 0:
            factors.append(d)
            p_1 //= d
        d += 1
    factors = [[i, factors.count(i)] for i in set(factors)]
    x = []
    for factor in factors:
        print("[x]", factor)
        c_i_list = []
        for i in range(factor[1]):
            if i != 0:
                beta = (beta * pow(g, -(c_i_list[-1] * (factor[0] ** (i - 1))), p)) % p
            else:
                beta = h
            e1 = pow(beta, (p-1) // (factor[0] ** (i + 1)), p)
            e2 = pow(g, (p-1) // factor[0], p)
            for c_i in (range(factor[0])):
                if pow(e2, c_i, p) == e1:
                    c_i_list.append(c_i)
                    break
        x.append(c_i_list)
    system = []
    for i, factor in enumerate(factors):
        res = 0
        for j, x_j in enumerate(x[i]):
            res += x_j * (factor[0] ** j)
        res = res % (factor[0] ** factor[1])
        system.append(res)
    factors = [factors[i][0] ** factors[i][1] for i in range(len(factors))]
    result = gf_crt(system, factors, ZZ)
    return result

xg=2251943082815531488928173203931606442352364961363587288724899012777
xh=3620329099657742062187693451873462737625932034695683084237035127743
xp=22954440473064692367638020521915192869513867655951252438024058919141
print(Pohlig_Hellman(xg, xh, xp))