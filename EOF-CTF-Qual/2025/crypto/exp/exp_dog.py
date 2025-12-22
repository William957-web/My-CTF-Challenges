from pwn import *
from tinyec import registry
from secrets import randbelow
from random import getrandbits
import os
from hashlib import sha256
import HashTools
from Crypto.Util.number import *

r = remote("127.0.0.1", 19081)
curve = registry.get_curve('secp256r1')
p = 115792089210356248762697446949407573530086143415290314195533631308867097853951
n = 115792089210356248762697446949407573529996955224135760342422259061068512044369
G = curve.g

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
    

state=[]

for i in range((32*624)//128):
    cur_id = obtain_id()
    while cur_id:
        state.append(untemper(cur_id & 0xffffffff))
        cur_id >>= 32
 
state.append(624)
random.setstate([3, tuple(state), None])

# print(random.getrandbits(128))
# r.interactive()    

r_1, s_1 = obtain_signature(b'whale120')
k_1 = random.getrandbits(255)
r_2, s_2 = obtain_signature(b'whale120')
k_2 = random.getrandbits(255)

secret = (((s_1*k_1%n) - (s_2*k_2%n)) * pow(r_1 - r_2, -1, n)) % n
Q = secret * G

origin_hash = long_to_bytes((s_1 * k_1 - r_1 * secret)% n)

h = HashTools.new(algorithm="sha256")
new_data, new_hash = h.extension(
    secret_length=64,
    original_data=b"whale120",
    append_data=b"i_am_the_king_of_the_dog",
    signature=origin_hash.hex()
)

print(new_data, new_hash)


def sign_msg(hashed_data_hex):
    z = int(hashed_data_hex, 16) % n
    k = getrandbits(255)
    R = k * G
    cur_r = R.x
    cur_s = (z + cur_r * secret) * pow(k, -1, n) % n
    return cur_r, cur_s

new_r, new_s = sign_msg(new_hash)

r.sendline(b'wowoOf')
r.sendline(hex(new_r).encode())
r.sendline(hex(new_s).encode())
r.sendline(new_data.hex().encode())
print(r.recvall().decode())
r.interactive()
