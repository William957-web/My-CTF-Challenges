from Crypto.Util.number import *
from flag import flag
import os
import random

assert len(flag) == 84

flag=flag

e = 0x10001
output = ''

def encrypt(msg):
    print(msg)
    global output
    m = bytes_to_long(msg)
    p = getPrime(20)
    c = pow(m, e, p)
    output += f"{p=}\n{c=}\n"

all_msg = []

for i in range(80):
    all_msg.append(flag)
    all_msg.append(os.urandom(84))

random.shuffle(all_msg)

for msg in all_msg:
    encrypt(msg)

f = open('output.txt', 'w')
f.write(output)
f.close()
