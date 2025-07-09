from hashlib import sha512
import random
from gmpy2 import iroot
from Crypto.Util.number import long_to_bytes

def untemper(rand):
    rand ^= rand >> 18
    rand ^= (rand << 15) & 0xefc60000
    a = rand ^ ((rand << 7) & 0x9d2c5680)
    b = rand ^ ((a << 7) & 0x9d2c5680)
    c = rand ^ ((b << 7) & 0x9d2c5680)
    d = rand ^ ((c << 7) & 0x9d2c5680)
    rand = rand ^ ((d << 7) & 0x9d2c5680)
    rand ^= ((rand ^ (rand >> 11)) >> 11)
    return rand

state = []

trials = [int.from_bytes(sha512(bytes([i])).digest()) for i in range(256)]
f = open('output.txt', 'r')
f = f.read().split('\n')
datas = []

for i in range(81):
    datas.append(int(f[i], 16))

#print(datas)

for i in range(80):
    for j in range(256):
        cur = datas[i]^trials[j]
        if iroot(cur, 2)[1]:
            cur = int(iroot(cur, 2)[0])
            for k in range(8):
                state.append(untemper(cur&0xffffffff))
                cur >>= 32

state = state[-624:]
state.append(624)
random.setstate([3, tuple(state), None])

flag = random.getrandbits(256)**2^datas[80]
print(long_to_bytes(flag))
