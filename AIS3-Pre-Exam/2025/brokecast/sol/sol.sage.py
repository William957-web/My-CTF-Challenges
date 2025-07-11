

# This file was *autogenerated* from the file sol.sage
from sage.all_cmdline import *   # import sage library

_sage_const_2 = Integer(2); _sage_const_80 = Integer(80); _sage_const_1 = Integer(1); _sage_const_0x10001 = Integer(0x10001); _sage_const_100 = Integer(100); _sage_const_84 = Integer(84); _sage_const_8 = Integer(8); _sage_const_0 = Integer(0)
from Crypto.Util.number import *
from gmpy2 import *

f = open('output.txt', 'r')
datas = f.read().split('\n')

ps = []
cs = []

for i in range(_sage_const_2 *_sage_const_80 ):
    p = int(datas[i*_sage_const_2 ].split('=')[_sage_const_1 ])
    c = int(datas[i*_sage_const_2 +_sage_const_1 ].split('=')[_sage_const_1 ])
    d = int(inverse(_sage_const_0x10001 , p-_sage_const_1 ))
    ps.append(p)
    cs.append(int(pow(c, d, p)))

R=crt(cs, ps)
N = _sage_const_1 

for i in ps:
    N*=i

P = PolynomialRing(Zmod(N), names=('x',)); (x,) = P._first_ngens(1)
f = x-R

for i in range(_sage_const_1 , _sage_const_100 ):
    flag = f.small_roots(X=_sage_const_2 **(_sage_const_84 *_sage_const_8 ), beta=i/_sage_const_100 )
    print(i)
    if len(flag)>_sage_const_0 :
        print(long_to_bytes(int(flag[_sage_const_0 ])))

