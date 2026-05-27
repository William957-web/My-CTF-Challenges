#!/usr/bin/env python3
import argparse
import hashlib
import os
import random

from shared.zkp import compute_proof, compute_proof_from_digest, encode_suffix, load_flag
from solve import OracleSolver, S, b64decode, solve_round


class FakeOracleTube:
    def __init__(self, digest: bytes):
        self.token = int.from_bytes(digest, "big")
        self.buf = b">\n"
        self.state = "menu"

    def recv_until(self, marker: bytes) -> bytes:
        while marker not in self.buf:
            raise EOFError(f"marker {marker!r} not available in fake tube buffer {self.buf!r}")
        index = self.buf.index(marker) + len(marker)
        out = self.buf[:index]
        self.buf = self.buf[index:]
        return out

    def recv_line(self) -> bytes:
        return self.recv_until(b"\n")

    def send_line(self, line: str) -> None:
        if self.state == "menu":
            if line == "1":
                self.buf += f"proof = {self.oracle(S)}\n".encode() + b">\n"
            elif line == "2":
                self.buf += b"bit index:\n"
                self.state = "await_bit"
            elif line == "3":
                return
            else:
                raise ValueError(f"unexpected menu choice {line!r}")
            return

        if self.state == "await_bit":
            index = int(line)
            self.flip_digest_bit(index)
            self.buf += b"bit flipped\n>\n"
            self.state = "menu"
            return

        raise ValueError(f"unexpected state {self.state!r}")

    def oracle(self, salt: int) -> int:
        value = 0
        for bit in f"{self.token:0256b}":
            if bit == "0":
                value += salt
            else:
                value = pow(value, salt, solve_modulus)
        return value

    def flip_digest_bit(self, index: int) -> None:
        if not 0 <= index < 256:
            raise ValueError(index)
        bit = 255 - index
        self.token ^= 1 << bit

    def close(self) -> None:
        return


solve_modulus = 528302026814581112698976132408136607344677298272713726039361987095410824358231139478581273


def run_length_search(flag: bytes, origin_hash: bytes, original_suffix: bytes, length_min: int, length_max: int, rounds: int):
    for secret_length in range(length_min, length_max + 1):
        ok = True
        for _ in range(rounds):
            server_suffix = os.urandom(32)
            seed = random.randrange(2, solve_modulus)
            forged_nonce_b64, forged_hash = solve_round(
                origin_hash=origin_hash,
                original_data=original_suffix,
                secret_length=secret_length,
                server_suffix_b64=encode_suffix(server_suffix),
            )
            forged_nonce = b64decode(forged_nonce_b64)
            submitted = compute_proof_from_digest(forged_hash, seed)
            expected = compute_proof(flag, forged_nonce + server_suffix, seed)
            if submitted != expected:
                ok = False
                break
        print(f"secret length {secret_length}: {'ok' if ok else 'wrong'}")
        if ok:
            return secret_length
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--flag-path", default="flag.txt")
    parser.add_argument("--secret-length-min", type=int, default=1)
    parser.add_argument("--secret-length-max", type=int, default=128)
    parser.add_argument("--rounds", type=int, default=16)
    parser.add_argument("--suffix-hex")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    flag = load_flag(args.flag_path)
    original_suffix = bytes.fromhex(args.suffix_hex) if args.suffix_hex else os.urandom(32)
    true_hash = hashlib.sha256(flag + original_suffix).digest()

    print(f"flag length = {len(flag)}")
    print(f"original suffix = {original_suffix.hex()}")
    print(f"true hash = {true_hash.hex()}")

    tube = FakeOracleTube(true_hash)
    solver = OracleSolver(tube=tube, verbose=args.verbose)
    leaked_hash = solver.solve_digest()
    print(f"leaked hash = {leaked_hash.hex()}")
    print(f"hash match = {leaked_hash == true_hash}")

    if leaked_hash != true_hash:
        print("oracle leak failed before challenge phase")
        return

    found = run_length_search(
        flag=flag,
        origin_hash=leaked_hash,
        original_suffix=original_suffix,
        length_min=args.secret_length_min,
        length_max=args.secret_length_max,
        rounds=args.rounds,
    )
    print(f"successful length = {found}")
    if found is not None:
        print(flag.decode())


if __name__ == "__main__":
    main()
