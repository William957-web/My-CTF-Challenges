import base64
import hashlib
import json
import random


E = 677676677


def is_prime(n):
    for _ in range(1337):
        if pow(random.randrange(1, n), n - 1, n) != 1:
            return False
    return True


def inverse(a, m):
    old_r, r = a, m
    old_s, s = 1, 0

    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
    return old_s


SMALL_PRIMES = (
    3, 5, 7, 11, 13, 17, 19, 23, 29, 31,
    37, 41, 43, 47, 53, 59, 61, 67, 71, 73,
    79, 83, 89, 97, 101, 103, 107, 109, 113,
)


def random_prime(bits):
    while True:
        n = random.getrandbits(bits)
        n |= 1 << (bits - 1)
        ok = True
        for p in SMALL_PRIMES:
            if n % p == 0:
                ok = False
                break
        if ok and is_prime(n):
            return n


def make_key(bits=512):
    p = random_prime(bits)
    q = random_prime(bits)
    while p == q:
        q = random_prime(bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    d = inverse(E, phi) % phi
    return {
        "n": n,
        "e": E,
        "d": d,
    }


KEY = make_key()


def b64e(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64d(data):
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def digest(data):
    return int.from_bytes(hashlib.sha256(data.encode()).digest(), "big")


def sign_jwt(payload):
    header = {"typ": "JWT", "alg": "RS256"}
    h = b64e(json.dumps(header, separators=(",", ":")).encode())
    p = b64e(json.dumps(payload, separators=(",", ":")).encode())
    body = h + "." + p
    sig = pow(digest(body), KEY["d"], KEY["n"])
    return body + "." + b64e(sig.to_bytes((KEY["n"].bit_length() + 7) // 8, "big"))


def verify_jwt(token):
    parts = token.split(".")
    if len(parts) != 3:
        return "Wrong"
    body = parts[0] + "." + parts[1]
    sig = int.from_bytes(b64d(parts[2]), "big")
    if pow(sig, KEY["e"], KEY["n"]) == digest(body):
        return "OK"
    return "Wrong"


def payload_bytes(token):
    return b64d(token.split(".")[1])


def payload_json(token):
    return json.loads(payload_bytes(token).decode())
