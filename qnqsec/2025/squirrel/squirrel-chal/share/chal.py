from helper import gen_primes, banner
from Crypto.Util.number import inverse, bytes_to_long
from collections import namedtuple

Point = namedtuple("Point", "x y")
O = 'Origin'
FLAG = 'QnQSec{i_really_really_really_really_really_really_really_like_u_:)_🎹🎼🐋}'.encode()

assert len(FLAG) == 81

def check_point(P: tuple):
    if P == O:
        return True
    else:
        return (P.y**2 - (P.x**3 + a*P.x + b)) % p == 0 and 0 <= P.x < p and 0 <= P.y < p


def point_inverse(P: tuple):
    if P == O:
        return P
    return Point(P.x, -P.y % p)


def point_addition(P: tuple, Q: tuple):
    if P == O:
        return Q
    elif Q == O:
        return P
    elif Q == point_inverse(P):
        return O
    else:
        if P == Q:
            lam = (3*P.x**2 + a)*inverse(2*P.y, p)
            lam %= p
        else:
            lam = (Q.y - P.y) * inverse((Q.x - P.x), p)
            lam %= p
    Rx = (lam**2 - P.x - Q.x) % p
    Ry = (lam*(P.x - Rx) - P.y) % p
    R = Point(Rx, Ry)
    assert check_point(R)
    return R


def double_and_add(P: tuple, n: int):
    Q = P
    R = O
    while n > 0:
        if n % 2 == 1:
            R = point_addition(R, Q)
        Q = point_addition(Q, Q)
        n = n // 2
    assert check_point(R)
    return R

ps = gen_primes()
p = ps[0]*ps[1]
a = 120
b = 1337

# Generator
g_x = 218
g_y = 3223
G = double_and_add(Point(g_x, g_y), 0x1337)

TRIALS = 7 # Lucky 7 ~
CHALLENGE = double_and_add(G, bytes_to_long(FLAG))

print(banner)
print("===========================================")
print(f"{G.x=}\n{G.y=}")
print("===========================================")
print("Challenge:")
print(f"{CHALLENGE.x=}\n{CHALLENGE.y=}")
print("===========================================")

while TRIALS:
    print("Give me the coefficient to do oracle ... uhh ... 🐿cle(🐿call)")
    coeff = int(input("🐿call> "))
    print("===========================================")
    INPUT = double_and_add(G, coeff)
    print("Result:")
    print(f"{INPUT.x=}\n{INPUT.y=}")
    print("===========================================")
    TRIALS -= 1

print("Bye Bye~")