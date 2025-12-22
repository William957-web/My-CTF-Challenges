from tinyec import registry
from secrets import randbelow
from random import getrandbits, seed
import os
from hashlib import sha256

curve = registry.get_curve('secp256r1')
p = 115792089210356248762697446949407573530086143415290314195533631308867097853951
n = 115792089210356248762697446949407573529996955224135760342422259061068512044369
G = curve.g
secret = randbelow(n)
Q = secret * G
salt = os.urandom(64)

def wOoFfFFF_wWwooF(wWwooF):
    z = int(sha256(salt + wWwooF).hexdigest(), 16) % n
    k = getrandbits(255)
    R = k * G
    r = R.x
    s = (z + r * secret) * pow(k, -1, n) % n
    return r, s

def WoOoFfF_wWwooF(wWwooF, r, s):
    z = int(sha256(salt + wWwooF).hexdigest(), 16) % n
    u1, u2 = z * pow(s, -1, n), r * pow(s, -1, n)
    R_2 = u1 * G + u2 * Q
    return R_2.x == r

print("=" * 33, "Woof WoOf WooF wOOf: Woof wOOoooF", "=" * 33) # Welcome to the DOG: Orient Garrison
print("wowoof > WOoF wOooOOOOf WooF") # 1 for getting a ticket!
print("wowooF > WoOF wOoFfFFF wOOf Woof") # 2 for signing a ticket!
print("wowoOf > WoOoFfF WWwwOOf wOOf Woof") # 3 for verifying you're the King of the DOG ... or the ticket ;P

while True:
    option = input("option > ") # option
    if option == "wowoof":
        print(f"WooFf wOOF {getrandbits(round(133.7))^getrandbits(round(133.7))}'f 🐕!") # You're the i's doggy!
    elif option == "wowooF":
        wWwooF = input("(WooOfFfFfF FF) > ") # (HEXED)
        wWwooF = bytes.fromhex(wWwooF)
        if b"i_am_the_king_of_the_dog" in wWwooF:
             print("👎 ^ w ^ 👎")
             continue
        cur_r, cur_s = wOoFfFFF_wWwooF(wWwooF)
        print(f"wwwooOf: {hex(cur_r)}")
        print(f"wwWooOf: {hex(cur_s)}")
        
    elif option == "wowoOf":
        cur_r = int(input("wwwooOf > "), 16)
        cur_s = int(input("wwWooOf > "), 16)
        wWwooF = input("(WooOfFfFfF FF) > ") # (HEXED)
        wWwooF = bytes.fromhex(wWwooF)
        
        if WoOoFfF_wWwooF (wWwooF, cur_r, cur_s):
            print("👍 ^ w ^ 👍")
            if b"i_am_the_king_of_the_dog" in wWwooF:
                with open("flag.txt") as f:
                     flag = f.read()
                     print(flag)
                     exit()
        else:
            print("👎 ^ w ^ 👎")
    
    else:
        print("🐾WoooF WoooF🐾")
        exit()
