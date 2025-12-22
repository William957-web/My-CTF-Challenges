from pwn import *
from tinyec import registry
from secrets import randbelow
from random import getrandbits
import os
from hashlib import sha256
import HashTools
from Crypto.Util.number import *
from sage.all import *
from gf2bv import LinearSystem
from gf2bv.crypto.mt import MT19937


r = remote("10.113.5.211", 19081)
curve = registry.get_curve('secp256r1')
p = 115792089210356248762697446949407573530086143415290314195533631308867097853951
n = 115792089210356248762697446949407573529996955224135760342422259061068512044369
G = curve.g


def obtain_id():
    # WooFf wOOF 324872494320987371404017360311352510115'f 🐕!
    r.recv()
    r.sendline(b'wowoof')
    res = r.recvline()
    return int(res.replace(b'WooFf wOOF ', b'').replace("'f 🐕!".encode(), b'').decode())

def obtain_signature(msg):
    r.recv()
    r.sendline(b'wowooF')
    r.recv()
    r.sendline(msg.hex().encode())
    res = r.recvline()
    cur_r = int(res.replace(b'wwwooOf: ', b'').decode(), 16)
    res = r.recvline()
    cur_s = int(res.replace(b'wwWooOf: ', b'').decode(), 16)
    return cur_r, cur_s

lin = LinearSystem([int(32)] * 624)
mt = lin.gens()
rng = MT19937(mt)
zeros = []

from tqdm import trange

for i in trange(200):
    zeros.append(rng.getrandbits(134) ^ rng.getrandbits(134) ^ int(obtain_id()))

zeros.append(mt[0] ^ int(0x80000000))
info("Solving states")
sol = lin.solve_one(zeros)
rng = MT19937(sol)
pyrand = rng.to_python_random()

for i in range(200):
    pyrand.getrandbits(134) ^ pyrand.getrandbits(134)

# print(pyrand.getrandbits(134) ^^ pyrand.getrandbits(134))
# r.interactive()    

r_1, s_1 = obtain_signature(b'whale120')
k_1 = pyrand.getrandbits(255)
r_2, s_2 = obtain_signature(b'whale120')
k_2 = pyrand.getrandbits(255)

secret = (((s_1*k_1%n) - (s_2*k_2%n)) * pow(r_1 - r_2, -1, n)) % n
Q = int(secret) * G

origin_hash = long_to_bytes((s_1 * k_1 - r_1 * secret)% n)

h = HashTools.new(algorithm="sha256")
new_data, new_hash = h.extension(
    secret_length=int(64),
    original_data=b"whale120",
    append_data=b"i_am_the_king_of_the_dog",
    signature=origin_hash.hex()
)

print(new_data, new_hash)


def sign_msg(hashed_data_hex):
    global pyrand
    z = int(hashed_data_hex, 16) % n
    k = pyrand.getrandbits(255)
    R = k * G
    cur_r = R.x
    cur_s = (z + cur_r * secret) * pow(k, -1, n) % n
    return cur_r, cur_s

new_r, new_s = sign_msg(new_hash)

r.sendline(b'wowoOf')
r.sendline(hex(new_r).encode())
r.sendline(hex(new_s).encode())
r.sendline(new_data.hex().encode())
# print(r.recv().decode())
r.interactive()
