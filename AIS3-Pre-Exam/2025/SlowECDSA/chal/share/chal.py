#!/usr/bin/env python3

import hashlib, os
from ecdsa import SigningKey, VerifyingKey, NIST192p
from ecdsa.util import number_to_string, string_to_number
from Crypto.Util.number import getRandomRange
from flag import flag

FLAG = flag

class LCG:
    def __init__(self, seed, a, c, m):
        self.state = seed
        self.a = a
        self.c = c
        self.m = m

    def next(self):
        self.state = (self.a * self.state + self.c) % self.m
        return self.state

curve = NIST192p
sk = SigningKey.generate(curve=curve)
vk = sk.verifying_key
order = sk.curve.generator.order()

lcg = LCG(seed=int.from_bytes(os.urandom(24), 'big'), a=1103515245, c=12345, m=order)

def sign(msg: bytes):
    h = int.from_bytes(hashlib.sha1(msg).digest(), 'big') % order
    k = lcg.next()
    R = k * curve.generator
    r = R.x() % order
    s = (pow(k, -1, order) * (h + r * sk.privkey.secret_multiplier)) % order
    return r, s

def verify(msg: str, r: int, s: int):
    h = int.from_bytes(hashlib.sha1(msg.encode()).digest(), 'big') % order
    try:
        sig = number_to_string(r, order) + number_to_string(s, order)
        return vk.verify_digest(sig, hashlib.sha1(msg.encode()).digest())
    except:
        return False

example_msg = b"example_msg"
print("==============SlowECDSA===============")
print("Available options: get_example, verify")

while True:
    opt = input("Enter option: ").strip()

    if opt == "get_example":
        print(f"msg: {example_msg.decode()}")
        example_r, example_s = sign(example_msg)
        print(f"r: {hex(example_r)}")
        print(f"s: {hex(example_s)}")

    elif opt == "verify":
        msg = input("Enter message: ").strip()
        r = int(input("Enter r (hex): ").strip(), 16)
        s = int(input("Enter s (hex): ").strip(), 16)

        if verify(msg, r, s):
            if msg == "give_me_flag":
                print("✅ Correct signature! Here's your flag:")
                print(FLAG.decode())
            else:
                print("✔️ Signature valid, but not the target message.")
        else:
            print("❌ Invalid signature.")

    else:
        print("Unknown option. Try again.")
