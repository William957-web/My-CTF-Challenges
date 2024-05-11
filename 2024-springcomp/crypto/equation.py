from Crypto.Util.number import *
import random

base=getPrime(512)
def func(x):
    return x**3+x**2+1337*x+base

while True:
    p=func(random.getrandbits(84))
    if isPrime(p):
        break

while True:
    q=func(random.getrandbits(84))
    if isPrime(q):
        break


n=p*q
e=65537
flag=b'ICED{c0pper_smith_ch33ring!!!}'
c=pow(bytes_to_long(flag), e, n)
print(f'{n=}\n{e=}\n{c=}\n{base=}\n')
