from Crypto.Util.number import *
from random import getrandbits

SIZE = 64
FLAG = bytes_to_long(b'NHNC{using_big_intergers_in_python_is_still_a_pain}')
e = 37
p, q = getPrime(1024), getPrime(1024)
while ((p-1)*(q-1)) % e == 0 :
    p, q = getPrime(1024), getPrime(1024)
N = p*q

print("=== ICEDTEA Verifier 1.0 ===")

while True:
    OTP = getrandbits(SIZE)
    print(f"signed: {pow(OTP, e, N)}")
    TRIAL = int(input("OTP: "))
    if TRIAL == OTP:
        print(f"signed: {pow(FLAG, e, N)}")
        continue    
        
    print(f"Invalid OTP, {OTP}")
