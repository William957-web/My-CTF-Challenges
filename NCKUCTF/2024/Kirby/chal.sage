from random import randint
from hashlib import sha256
FLAG=b'NCKUCTF{chummy==kirby}\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
def xor(b1: bytes, b2: bytes):
    return bytes([x ^^ y for x, y in zip(b1, b2)])

p = 2557088666494490131660800000000000001
a = 1323879184140127113148715489137793
b = 1413453335371254304533447979395016
E = EllipticCurve(GF(p), [a, b])
G = E.gens()[0]
kirby_secret, system_secret = randint(1, E.order()-1), randint(1, E.order()-1)
kirby_public, system_public = G*kirby_secret, G*system_secret
print(f">> System: {G.xy()}")
print(f">> Kirby: {kirby_public.xy()}")
print(f">> System: {system_public.xy()}")
key = system_secret*kirby_public.xy()[0]
key = sha256(str(key).encode()).digest()
print(f">> Kirby: {xor(key, FLAG).hex()}")