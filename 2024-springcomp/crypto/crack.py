'''
leak:6c0b4b76b562225f19ff5f62186f5384
test_ciphertext='50c3396d24d6a207c43f343adbfe2e00'
flag_ciphertext='933f2c449f0f040680723ab7c6cdfd90c1860e1d3dbbeacaf66f1074ffca7bef75a93aae837ba0f7a3b9d713e4e1c0437d8cb4e6ed5b53a96fd458b01d4f0b0649c1f426634675fe25d5abc085edefda'
'''
from Crypto.Cipher import AES
from tqdm import *

def pad(m):
    padlen = -len(m) % 16
    return m + bytes([0] * padlen)

key=b'whaleshark'
msg1=b'TEST~1, 2, 3'
leak1=bytes.fromhex('50c3396d24d6a207c43f343adbfe2e00')
testing={b'1'}
form={b'1':b'1'}
flag=bytes.fromhex('933f2c449f0f040680723ab7c6cdfd90c1860e1d3dbbeacaf66f1074ffca7bef75a93aae837ba0f7a3b9d713e4e1c0437d8cb4e6ed5b53a96fd458b01d4f0b0649c1f426634675fe25d5abc085edefda')
for i in trange(100000, 999999):
    aes=AES.new(key+str(i).encode(), AES.MODE_ECB)
    testing.add(aes.encrypt(pad(msg1)))
    form[aes.encrypt(pad(msg1))]=i

for i in trange(100000, 999999):
    aes=AES.new(key+str(i).encode(), AES.MODE_ECB)
    if aes.decrypt(leak1) in testing:
        aes1=AES.new(key+str(form[aes.decrypt(leak1)]).encode(), AES.MODE_ECB)
        print(aes1.decrypt(aes.decrypt(flag)))
        break
