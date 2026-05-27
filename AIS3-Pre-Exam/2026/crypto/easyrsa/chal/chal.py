from Crypto.Util.number import *

flag = b'AIS3{easy_rsa_easy_algebra_easy_aislop_easy_easy_easy_on_its_way_qaq}'

p = getPrime(512)
q = (p**2+1)
r = getPrime(2048)
e = 677676677
N = p*q*r
c = pow(bytes_to_long(flag), e, N)

print(f"{e=}\n{c=}\n{N*getPrime(512)=}")
