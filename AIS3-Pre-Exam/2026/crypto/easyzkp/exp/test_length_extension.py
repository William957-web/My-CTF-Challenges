#!/usr/bin/env python3
import argparse
import hashlib
import os

from shared.zkp import N, compute_proof, compute_proof_from_digest, encode_suffix, load_flag
from solve import b64decode, solve_round


ROUND_COUNT = 16


def simulate_challenge(
    flag: bytes,
    origin_hash: bytes,
    original_suffix: bytes,
    secret_length: int,
    rounds: int,
    verbose: bool,
) -> bool:
    for round_index in range(1, rounds + 1):
        server_suffix = os.urandom(32)
        server_suffix_b64 = encode_suffix(server_suffix)
        forged_nonce_b64, forged_hash = solve_round(
            origin_hash=origin_hash,
            original_data=original_suffix,
            secret_length=secret_length,
            server_suffix_b64=server_suffix_b64,
        )
        forged_nonce = b64decode(forged_nonce_b64)
        seed = int.from_bytes(os.urandom(32), "big") % (N - 2) + 2
        submitted = compute_proof_from_digest(forged_hash, seed)
        expected = compute_proof(flag, forged_nonce + server_suffix, seed)
        ok = submitted == expected
        if verbose:
            print(
                f"round {round_index:02d}: len={secret_length} "
                f"nonce_bytes={len(forged_nonce)} ok={ok}"
            )
        if not ok:
            return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--flag-path", default="flag.txt")
    parser.add_argument("--origin-hash")
    parser.add_argument("--original-suffix-hex")
    parser.add_argument("--secret-length", type=int)
    parser.add_argument("--secret-length-min", type=int, default=1)
    parser.add_argument("--secret-length-max", type=int, default=128)
    parser.add_argument("--rounds", type=int, default=ROUND_COUNT)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    flag = load_flag(args.flag_path)

    if args.original_suffix_hex is not None:
        original_suffix = bytes.fromhex(args.original_suffix_hex)
    else:
        original_suffix = os.urandom(32)

    if args.origin_hash is not None:
        origin_hash = bytes.fromhex(args.origin_hash)
    else:
        origin_hash = hashlib.sha256(flag + original_suffix).digest()

    if args.secret_length is not None:
        lengths = [args.secret_length]
    else:
        lengths = list(range(args.secret_length_min, args.secret_length_max + 1))

    print(f"flag length = {len(flag)}")
    print(f"original suffix = {original_suffix.hex()}")
    print(f"origin hash = {origin_hash.hex()}")

    successes = []
    for secret_length in lengths:
        ok = simulate_challenge(
            flag=flag,
            origin_hash=origin_hash,
            original_suffix=original_suffix,
            secret_length=secret_length,
            rounds=args.rounds,
            verbose=args.verbose,
        )
        print(f"secret length {secret_length}: {'ok' if ok else 'wrong'}")
        if ok:
            successes.append(secret_length)

    print(f"successful lengths = {successes}")


if __name__ == "__main__":
    main()
