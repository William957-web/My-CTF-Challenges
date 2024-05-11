from Crypto.Cipher import AES
from random import randint
from hashlib import md5
def pad(m):
    padlen = -len(m) % 16
    return m + bytes([0] * padlen)

key=b'whaleshark'
key1 = key+str(randint(100000, 999999)).encode()
key2 = key+str(randint(100000, 999999)).encode()
aes1 = AES.new(key1, AES.MODE_ECB)
aes2 = AES.new(key2, AES.MODE_ECB)

test_msg=b'TEST~1, 2, 3'
test_ciphertext=aes2.encrypt(aes1.encrypt(pad(test_msg))).hex()

flag_msg=b'ICED{MitM_is_both_Man_in_the_Middle_Attack_and_Meet_in_the_Middle_Attack!}'
flag_ciphertext=aes2.encrypt(aes1.encrypt(pad(flag_msg))).hex()

print(f'leak:{md5(key).hexdigest()}')
print(f'{test_ciphertext=}')
print(f'{flag_ciphertext=}')
