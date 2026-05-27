from hashlib import shake_256
from math import gcd
from secrets import randbelow, randbits

from Crypto.Util.number import bytes_to_long, getPrime, inverse

flag = b"AIS3{TEST_ME}"
BITS = 448
ROUNDS = 896
NBITS = 32
NROWS = 72
SETS = 2
WIDTH = 192
MODBITS = 256
SMALL = 12
PRIMEBITS = 3 * BITS


def gen():
    m = bytes_to_long(flag)
    while True:
        p = getPrime(PRIMEBITS)
        q = getPrime(PRIMEBITS)
        n = p * q
        phi = (p - 1) * (q - 1)
        d = randbits(BITS - 1) | (1 << (BITS - 1)) | 1
        if m < n and gcd(m, n) == 1 and gcd(d, phi) == 1:
            e = inverse(d, phi)
            c = pow(m, e, n)
            return c, n, d


def f(base, idx):
    buf = shake_256(base.to_bytes(WIDTH // 8, "big") + idx.to_bytes(4, "big")).digest(BITS // 8)
    return int.from_bytes(buf, "big")


def bundle(base):
    rows = [randbits(NBITS) for _ in range(NROWS)]
    cols = [[(row >> i) & 1 for row in rows] for i in range(NBITS)]
    out = []
    for _ in range(SETS):
        mod = getPrime(MODBITS)
        coeffs = [randbelow(mod) for _ in range(NBITS)]
        bias = [randbits(SMALL - 1) | (1 << (SMALL - 1)) for _ in range(NROWS)]
        vals = []
        for j in range(NROWS):
            total = -base * bias[j]
            for i in range(NBITS):
                total += coeffs[i] * cols[i][j]
            vals.append(total % mod)
        out.append((mod, bias, vals))
    return out


c, n, d = gen()
rows = [randbits(BITS) for _ in range(ROUNDS)]
base = randbits(WIDTH - 1) | (1 << (WIDTH - 1))

print(f"c = {c}")
print("blob = [")
for item in bundle(base):
    print(f"    {item},")
print("]")
print("data = [")
for i, row in enumerate(rows):
    print(f"    ({row ^ f(base, i)}, {pow(c, d ^ row, n)}),")
print("]")
