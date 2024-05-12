from Crypto.Util.number import *
flag=b'THJCC{small_eeeee_can_be_pwned_easily}'
m=bytes_to_long(flag)
p=getPrime(512)
q=getPrime(512)
n=p*q
phi=(p-1)*(q-1)
e=3
c=pow(m, e, n)
print(f'{n=}, {e=}')
print(f'{c=}')