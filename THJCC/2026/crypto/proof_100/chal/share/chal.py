from flags import flag
from Crypto.Util.number import *
from hashlib import md5
import os

p, q = getPrime(64), getPrime(64)
e = 0x10001
N = p * q
d = pow(e, -1, (p-1)*(q-1))

seed = os.urandom(16)

def sign(msg):
    global d, N
    m = bytes_to_long(md5(msg).digest())
    return pow(m, d, N)

used_keys = []
print(f"SEED: {seed.hex()}")
print(f"{e=}")

for i in range(100):
    print("My turn owo")
    cur_key = bytes.fromhex(input("key:"))
    print(sign(cur_key+seed))
    used_keys.append(cur_key)
    print("Your turn ^w^")
    cur_key = bytes.fromhex(input("key:"))
    if cur_key in used_keys:
        print("Can u be more creative LOL")
        exit()
    
    proof = int(input("proof:"))
    if proof != sign(cur_key+seed):
        print("Sorry u didn't proof anything ...")
        exit()
    used_keys.append(cur_key)
    print("PASS!")

phi = int(input("phi?"))

if phi != (p-1)*(q-1):
    print("FAILED at LAST haha")
    exit()

print("Well done", flag)
