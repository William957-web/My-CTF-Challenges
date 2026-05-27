import json
import secrets
import sys
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from shared.zkp import N, compute_proof, decode_suffix, encode_suffix, load_flag

FLAG = load_flag()
ROUND_COUNT = 16
PROVER_URL = "http://web:5000/prove"
SUBORACLE_LIMIT = 128


def println(message=""):
    sys.stdout.write(message + "\n")
    sys.stdout.flush()


def read_line():
    data = sys.stdin.readline()
    if not data:
        raise EOFError
    return data.rstrip("\n")


def fetch_proof(user_part_b64, server_part_b64, seed, bit_flip_indices=None):
    flip_query = ""
    if bit_flip_indices is not None:
        for index in bit_flip_indices:
            flip_query += f"&f={index}"
    url = f"{PROVER_URL}?p={server_part_b64}{flip_query}&d={user_part_b64}&s={seed}"
    with urlopen(url, timeout=5) as response:
        payload = json.loads(response.read().decode())
    proof = payload.get("proof")
    if not isinstance(proof, int):
        raise ValueError("invalid prover response")
    return proof


def build_nonce():
    server_part = secrets.token_bytes(32)
    server_part_b64 = encode_suffix(server_part)
    println(f"server suffix = {server_part_b64}")
    println("nonce:")
    user_part_b64 = read_line().strip()
    return user_part_b64, server_part_b64


def option_oracle():
    try:
        user_part_b64, server_part_b64 = build_nonce()
        seed = secrets.randbelow(N - 2) + 2
    except Exception:
        println("invalid request")
        return
    flipped_indices = []
    get_proof_remaining = SUBORACLE_LIMIT
    flip_remaining = SUBORACLE_LIMIT
    while True:
        println("oracle:")
        println(f"1. HTTP get proof ({get_proof_remaining} left)")
        println(f"2. flip one sha256 bit ({flip_remaining} left)")
        println("3. exit")
        println(">")
        try:
            choice = read_line().strip()
            if choice == "1":
                if get_proof_remaining == 0:
                    println("HTTP oracle exhausted")
                    continue
                proof = fetch_proof(
                    user_part_b64,
                    server_part_b64,
                    seed,
                    bit_flip_indices=flipped_indices,
                )
                get_proof_remaining -= 1
                println(f"proof = {proof}")
            elif choice == "2":
                if flip_remaining == 0:
                    println("flip oracle exhausted")
                    continue
                println("bit index:")
                index = int(read_line().strip())
                if not 0 <= index < 256:
                    raise ValueError
                flipped_indices.append(index)
                flip_remaining -= 1
                println("bit flipped")
            elif choice == "3":
                return
            else:
                println("bye")
                return
        except Exception:
            println("invalid request")
            return


def option_challenge():
    println(f"pass {ROUND_COUNT} rounds.")
    for index in range(1, ROUND_COUNT + 1):
        println(f"round {index}/{ROUND_COUNT}")
        try:
            shown_nonce, server_part_b64 = build_nonce()
            suffix = decode_suffix(shown_nonce) + decode_suffix(server_part_b64)
            seed = secrets.randbelow(N - 2) + 2
            expected = compute_proof(FLAG, suffix, seed)
        except Exception:
            println("error")
            return
        println(f"nonce = {shown_nonce}")
        println(f"seed = {seed}")
        println("proof:")
        answer = read_line().strip()
        if answer != str(expected):
            println("wrong")
            return
        println("ok")
    println(FLAG.decode())
    exit()

def main():
    println("1. ask prover")
    println("2. challenge")
    println(">")
    try:
        choice = read_line().strip()
        if choice == "1":
            option_oracle()
        elif choice == "2":
            option_challenge()
        else:
            println("bye")
            exit()
    except (EOFError, KeyboardInterrupt):
        return
    except (HTTPError, URLError):
        println("prover offline")


if __name__ == "__main__":
    while 'whale120'[:5] == 'whale':
        main()
