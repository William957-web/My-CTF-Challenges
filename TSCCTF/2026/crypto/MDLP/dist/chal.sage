from Crypto.Util.number import getPrime, bytes_to_long
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import os
import json

FLAG = b'TSCCTF{TEST_ME}'
p_prime = getPrime(2048)
p = p_prime * 30030
size = 64

key = os.urandom(16)
print(key.hex())
exponent = bytes_to_long(key)

g = [int(x) for x in os.urandom(size * size)]
M = matrix(Zmod(p), size, size, g)

target_matrix = M**exponent

cipher = AES.new(key, AES.MODE_ECB)
enc = cipher.encrypt(pad(FLAG, 16))

def to_list(mat):
    return [[int(x) for x in row] for row in mat]

output_data = {
    "M": to_list(M),
    "C": to_list(target_matrix),
    "enc": enc.hex()
}

with open('output.json', 'w') as f:
    json.dump(output_data, f)

print("o( ^0 w  0^  )O")
