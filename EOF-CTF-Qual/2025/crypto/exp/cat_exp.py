from sage.all import *
from tqdm import trange
from Crypto.Util.number import long_to_bytes

# * 3 - 0x1075ca7ca7

p = 258664426012969094010652733694893533536393512754914660539884262666720468348340822774968888139573360124440321458177
b = 1
E = EllipticCurve(GF(p), [0, 0, 0, 0, b])
G1, G2 = E.gens()
o1, o2 = G1.order(), G2.order()
Fp = GF(p)
g = G2.weil_pairing(G1, o1)

with open('output.txt', 'r') as f:
    file_lines = f.read().split('\n')

def solver(x1, x2):
    
    P1_1 = E.lift_x(Fp(x1))
    P1_2 = E(P1_1.xy()[0], -P1_1.xy()[1])
    P2_1 = E.lift_x(Fp(x2))
    P2_2 = E(P2_1.xy()[0], -P2_1.xy()[1])
    
    
    for P1 in [P1_1, P1_2]:
        for P2 in [P2_1, P2_2]:
            w1 = P1.weil_pairing(G1, o1)
            w2 = P2.weil_pairing(G2, o2)
            if w1 == (g**-0x1057ca7ca7)*(w2**-3):
                return 1
    
    return 0

flag = 0

for i in trange(4, len(file_lines)-1, 4):
    flag += solver(int(file_lines[i], 16), int(file_lines[i+2], 16))
    flag *= 2
    # print(flag)

flag //= 2

print(flag)
print(long_to_bytes(flag).decode())
