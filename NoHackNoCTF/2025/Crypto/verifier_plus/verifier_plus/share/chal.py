from Crypto.Util.number import *
from random import getrandbits

SIZE = 65
FLAG = bytes_to_long(b'NHNC{errors_lead_to_lll_huh_?_what_are_u_thinking_about}')
e = 37
p, q = getPrime(1024), getPrime(1024)
while ((p-1)*(q-1)) % e == 0 :
    p, q = getPrime(1024), getPrime(1024)
N = p*q

print("=== ICEDTEA Verifier 1.1 ===")

while True:
    OTP = getrandbits(SIZE)
    print(f"signed: {pow(OTP, e, N)}")
    TRIAL = int(input("OTP: "))
    if TRIAL == OTP:
        super_secret = getrandbits(1024)
        print(f"signed: {pow(FLAG + super_secret, e, N)}")
        continue
        
    print(f"Invalid OTP, {OTP}")
