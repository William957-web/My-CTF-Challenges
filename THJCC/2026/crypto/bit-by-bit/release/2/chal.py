from Crypto.Util.number import *
from flags import flag
import os, json

flag = flag.replace(b'THJCC{', b'').replace(b'}', b'')
assert len(flag) == 105, 'womp'
key = os.urandom(500)

def enc(msg):
    p, q = getPrime(32), getPrime(32)
    N = p * q
    e = 0x10001
    return [pow(bytes_to_long(msg), e, N), N]

output_data = []

for i in ''.join([format(b, '08b') for b in flag]):
    if i == '1':
        output_data.append(enc(key))
    elif i == '0':
        output_data.append(enc(os.urandom(500)))

with open('output.txt', 'w') as f:
    json.dump(output_data, f)
