from random import getrandbits
from os import urandom
from flags import flag

key = urandom(8)
# key = b'\x80'*8
key_bin = ''.join([format(b, '08b') for b in key])
p = 3134585081
e = 0x11
E = 0x10001

for i in range(512):
    idx = int(input('>'))
    cur_key = getrandbits(32)
    cur_state = key[idx//8]
    cur_salt = ((cur_key^cur_state)**e%p)^cur_state
    if key_bin[idx] == '1':
        cur_salt = (cur_salt**E)%p
        cur_salt^=cur_state
        print(cur_salt)
    else:
        print(cur_salt)

trial = input('?')
if bytes.fromhex(trial) == key:
    print(flag)

else:
    print('.w.')
