from random import getrandbits
import os
from hashlib import sha512
from flag import flag

def hexor(a: bytes, b: int):
    return hex(int.from_bytes(a)^b**2)

for i in range(80):
    print(hexor(sha512(os.urandom(True)).digest(), getrandbits(256)))

print(hexor(flag, getrandbits(256)))
