from Crypto.Util.number import *
from gmpy2 import *

f = open('output.txt', 'r')
datas = f.read().split('\n')

ps = []
cs = []

for i in range(2*80):
    p = int(datas[i*2].split('=')[1])
    c = int(datas[i*2+1].split('=')[1])
    d = int(inverse(0x10001, p-1))
    ps.append(p)
    cs.append(int(pow(c, d, p)))

R=crt(cs, ps)
N = 1

for i in ps:
    N*=i

P.<x> = PolynomialRing(Zmod(N))
f = x-R

for i in range(1, 100):
    flag = f.small_roots(X=2**(84*8), beta=i/100)
    print(i)
    if len(flag)>0:
        print(long_to_bytes(int(flag[0])))
