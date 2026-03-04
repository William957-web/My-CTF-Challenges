from pwn import *
from tqdm import trange
import time
r = remote('172.31.0.2', 40013)

def list_to_hex(bit_list):
    res_bytes = []
    for i in range(0, 64, 8):
        byte_bits = bit_list[i:i+8]
        byte_val = int(''.join(map(str, byte_bits)), 2)
        res_bytes.append(byte_val)
    
    return bytes(res_bytes).hex()

mapping = {}

for i in trange(8):
    for j in trange(64):
        st = time.time()
        r.sendline(str(j).encode())
        r.recvline()
        fi = time.time()
        if j not in mapping:
            mapping[j] = fi-st
        else:
            mapping[j] += fi-st

mn = 0x1000000

for i in range(64):
    mn = min(mn, mapping[i])

for i in range(64):
    mapping[i] -= mn

print(mapping)

threshold = float(input('(threshold)>'))
ans = []
for i in range(64):
    if mapping[i]>threshold:
        ans.append(1)
    else:
        ans.append(0)



r.sendline(list_to_hex(ans).encode())
r.interactive()
