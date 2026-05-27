#!/usr/bin/env python3
import argparse
import base64
import hashlib
import os
import socket
import sys
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass

from tqdm import trange
import HashTools

from shared.zkp import compute_proof, compute_proof_from_digest, load_flag


N = 528302026814581112698976132408136607344677298272713726039361987095410824358231139478581273
P = 725150593990274719678916870531826926518549387
S = 5175996367017249359
PROBE_SALT = 3


def is_s_residue_mod_p(x: int) -> bool:
    x %= P
    return x == 0 or pow(x, (P - 1) // S, P) == 1


def oracle_local(token: int, salt: int) -> int:
    value = 0
    for bit in bin(token)[2:]:
        if bit == "0":
            value += salt
        else:
            value = pow(value, salt, N)
    return value


class Tube:
    def __init__(self, host: str, port: int):
        self.sock = socket.create_connection((host, port), timeout=10)
        self.buf = b""

    def recv_until(self, marker: bytes) -> bytes:
        while marker not in self.buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise EOFError(f"connection closed while waiting for {marker!r}")
            self.buf += chunk
        index = self.buf.index(marker) + len(marker)
        out = self.buf[:index]
        self.buf = self.buf[index:]
        return out

    def recv_line(self) -> bytes:
        return self.recv_until(b"\n")

    def send_line(self, line: str) -> None:
        self.sock.sendall(line.encode() + b"\n")

    def close(self) -> None:
        self.sock.close()


class WrongSecretLength(RuntimeError):
    pass


@dataclass
class OracleSolver:
    tube: Tube
    verbose: bool = False
    used_get: int = 0
    used_flip: int = 0

    def log(self, message: str) -> None:
        if self.verbose:
            print(message, file=sys.stderr, flush=True)

    def _menu(self) -> None:
        self.tube.recv_until(b">\n")

    def oracle(self, salt: int) -> int:
        self._menu()
        self.tube.send_line("1")
        line = self.tube.recv_line().decode().strip()
        assert line.startswith("proof = "), line
        self.used_get += 1
        value = int(line.split(" = ", 1)[1])
        self.log(f"oracle({salt}) -> {value}")
        return value

    def flip_bit(self, bit: int) -> None:
        self._menu()
        self.tube.send_line("2")
        self.tube.recv_until(b"bit index:\n")
        index = 255 - bit
        self.tube.send_line(str(index))
        line = self.tube.recv_line().decode().strip()
        assert line == "bit flipped", line
        self.used_flip += 1
        self.log(f"flip bit {bit} (digest index {index})")

    def solve_digest(self) -> bytes:
        recovered_low = 0
        recovered_count = 0
        while True:
            if self.used_get >= 128:
                raise RuntimeError("proof budget exhausted")
            y = self.oracle(S)
            if y == 256 * S:
                self.log("oracle returned 256*S, so every remaining digest bit is 0")
                break
            hit = None
            for bit in range(256):
                z = y - bit * S
                if is_s_residue_mod_p(z):
                    hit = (bit, z)
                    break
            if hit is None:
                raise RuntimeError("no residue hit found")
            bit, z = hit
            if (recovered_low >> bit) & 1:
                # We already flipped this bit? This shouldn't happen if we only flip 1s to 0s.
                # But our logic might be flipping a bit back if we are not careful.
                # Actually, the residue logic finds the LAST 1-bit.
                # If we flip it to 0, it's no longer the last 1-bit.
                # So we should never hit the same bit twice.
                raise RuntimeError(f"already recovered bit {bit}")
            recovered_low |= 1 << bit
            recovered_count += 1
            self.log(
                f"recovered bit {bit:3d} | recovered={recovered_count:3d} "
                f"| get={self.used_get:3d}/128 flip={self.used_flip:3d}/128"
            )
            if self.used_flip >= 128:
                self.log("flip budget exhausted, attempting reconstruction with what we have")
                break
            self.flip_bit(bit)

        digest_int = recovered_low & ((1 << 256) - 1)
        self.log(
            f"digest reconstruction complete | ones={digest_int.bit_count()} "
            f"| get={self.used_get}/128 flip={self.used_flip}/128"
        )
        return digest_int.to_bytes(32, "big")


def b64decode(data: str) -> bytes:
    return base64.urlsafe_b64decode(data.encode())


def b64encode(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("latin-1")
    return base64.urlsafe_b64encode(data).decode()


def solve_round(origin_hash: bytes, original_data: bytes, secret_length: int, server_suffix_b64: str) -> tuple[str, bytes]:
    server_suffix = b64decode(server_suffix_b64)
    tool = HashTools.new(algorithm="sha256")
    new_data, new_hash = tool.extension(
        secret_length=secret_length,
        original_data=original_data,
        append_data=server_suffix,
        signature=origin_hash.hex(),
    )
    if isinstance(new_data, str):
        new_data = new_data.encode("latin-1")
    if isinstance(new_hash, str):
        new_hash = bytes.fromhex(new_hash)
    forged_prefix = new_data[:-len(server_suffix)] if server_suffix else new_data
    return b64encode(forged_prefix), new_hash


def build_secret_lengths(args: argparse.Namespace) -> list[int]:
    if args.secret_length is not None:
        return [args.secret_length]
    if args.secret_length_min <= 0:
        raise ValueError("secret length minimum must be positive")
    if args.secret_length_max < args.secret_length_min:
        raise ValueError("secret length maximum must be >= minimum")
    return list(range(args.secret_length_min, args.secret_length_max + 1))


def run_self_test(flag_path: str) -> None:
    flag = load_flag(flag_path)
    original_data = os.urandom(32)
    server_suffix = os.urandom(32)
    seed = 123456789
    origin_hash = hashlib.sha256(flag + original_data).digest()
    forged_nonce_b64, forged_hash = solve_round(
        origin_hash=origin_hash,
        original_data=original_data,
        secret_length=len(flag),
        server_suffix_b64=b64encode(server_suffix),
    )
    forged_nonce = b64decode(forged_nonce_b64)
    forged_proof = compute_proof_from_digest(forged_hash, seed)
    expected_proof = compute_proof(flag, forged_nonce + server_suffix, seed)
    if forged_proof != expected_proof:
        raise SystemExit("self-test failed: forged proof does not match expected proof")
    print("self-test ok")
    print(f"flag length = {len(flag)}")
    print(f"forged nonce bytes = {len(forged_nonce)}")
    print(f"forged digest = {forged_hash.hex()}")


def run_challenge_attempt(
    tube: Tube,
    origin_hash: bytes,
    original_data: bytes,
    secret_length: int,
    attempt: int,
    verbose: bool,
) -> str:
    prefix = "server suffix = "
    tube.recv_until(b">\n")
    tube.send_line("2")
    tube.recv_until(b"pass 16 rounds.\n")
    if verbose:
        print(
            f"[attempt {attempt}] trying challenge with secret length = {secret_length}",
            file=sys.stderr,
            flush=True,
        )

    for round_index in range(1, 17):
        round_line = tube.recv_line().decode().strip()
        assert round_line == f"round {round_index}/16", round_line

        line = tube.recv_line().decode().strip()
        assert line.startswith(prefix), line
        server_suffix_b64 = line[len(prefix):]
        if verbose:
            print(
                f"[attempt {attempt}] round {round_index:02d}: received server suffix {server_suffix_b64}",
                file=sys.stderr,
                flush=True,
            )

        tube.recv_until(b"nonce:\n")
        forged_nonce_b64, forged_hash = solve_round(
            origin_hash=origin_hash,
            original_data=original_data,
            secret_length=secret_length,
            server_suffix_b64=server_suffix_b64,
        )
        if verbose:
            print(
                f"[attempt {attempt}] round {round_index:02d}: sending forged nonce "
                f"({len(b64decode(forged_nonce_b64))} bytes after extension)",
                file=sys.stderr,
                flush=True,
            )
        tube.send_line(forged_nonce_b64)

        nonce_line = tube.recv_line().decode().strip()
        assert nonce_line.startswith("nonce = "), nonce_line
        seed_line = tube.recv_line().decode().strip()
        assert seed_line.startswith("seed = "), seed_line
        seed = int(seed_line.split(" = ", 1)[1])
        answer = compute_proof_from_digest(forged_hash, seed)
        tube.recv_until(b"proof:\n")
        tube.send_line(str(answer))

        result = tube.recv_line().decode().strip()
        if result != "ok":
            if verbose:
                print(
                    f"[attempt {attempt}] round {round_index:02d}: rejected with {result!r}",
                    file=sys.stderr,
                    flush=True,
                )
            raise WrongSecretLength(f"secret length {secret_length} rejected at round {round_index}: {result}")
        if verbose:
            print(f"[attempt {attempt}] round {round_index:02d}: ok", file=sys.stderr, flush=True)

    final_line = tube.recv_line().decode().strip()
    if verbose:
        print(f"[attempt {attempt}] success with secret length = {secret_length}", file=sys.stderr, flush=True)
    return final_line


def solve_attempt(
    host: str,
    port: int,
    secret_lengths: list[int],
    attempt: int,
    attempts_total: int,
    verbose: bool,
) -> str:
    prefix = "server suffix = "
    tube = Tube(host, port)
    try:
        if verbose:
            print(
                f"[attempt {attempt}/{attempts_total}] connect {host}:{port} "
                f"| oracle leak first, then trial {len(secret_lengths)} secret lengths",
                file=sys.stderr,
                flush=True,
            )

        tube.recv_until(b">\n")
        tube.send_line("1")

        line = tube.recv_line().decode().strip()
        assert line.startswith(prefix), line
        original_suffix_b64 = line[len(prefix):]
        original_data = b64decode(original_suffix_b64)
        if verbose:
            print(
                f"[attempt {attempt}] oracle bootstrap suffix bytes = {len(original_data)}",
                file=sys.stderr,
                flush=True,
            )

        tube.recv_until(b"nonce:\n")
        tube.send_line(f"&s={S}")

        solver = OracleSolver(tube=tube, verbose=verbose)
        origin_hash = solver.solve_digest()
        if verbose:
            print(f"[attempt {attempt}] recovered hash = {origin_hash.hex()}", file=sys.stderr, flush=True)
            print(f"[attempt {attempt}] original suffix = {original_data!r}", file=sys.stderr, flush=True)

        solver._menu()
        tube.send_line("3")
        last_error = None
        for secret_length in secret_lengths:
            try:
                return run_challenge_attempt(
                    tube=tube,
                    origin_hash=origin_hash,
                    original_data=original_data,
                    secret_length=secret_length,
                    attempt=attempt,
                    verbose=verbose,
                )
            except WrongSecretLength as exc:
                last_error = exc
                if verbose:
                    print(f"[attempt {attempt}] {exc}", file=sys.stderr, flush=True)
        if last_error is None:
            raise RuntimeError("no secret lengths were provided")
        raise last_error
    finally:
        tube.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=10000)
    parser.add_argument("--secret-length", type=int)
    parser.add_argument("--secret-length-min", type=int, default=1)
    parser.add_argument("--secret-length-max", type=int, default=128)
    parser.add_argument("--attempts", type=int, default=50)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--flag-path", default="flag.txt")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test(args.flag_path)
        return

    if args.workers <= 0:
        raise SystemExit("--workers must be positive")

    secret_lengths = build_secret_lengths(args)
    last_error = None

    if args.workers == 1:
        progress = trange(1, args.attempts + 1, disable=args.verbose)
        for attempt in progress:
            try:
                print(
                    solve_attempt(
                        host=args.host,
                        port=args.port,
                        secret_lengths=secret_lengths,
                        attempt=attempt,
                        attempts_total=args.attempts,
                        verbose=args.verbose,
                    )
                )
                return
            except Exception as exc:
                last_error = exc
                if args.verbose:
                    print(f"[attempt {attempt}] failed: {exc!r}", file=sys.stderr, flush=True)
        raise SystemExit(str(last_error))

    if args.verbose:
        print(
            f"parallel mode | workers={args.workers} | lengths={secret_lengths[0]}..{secret_lengths[-1]} "
            f"| attempts={args.attempts} leak sessions",
            file=sys.stderr,
            flush=True,
        )

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures: dict = {}
        next_attempt = 1

        def submit_attempt(attempt: int) -> None:
            future = executor.submit(
                solve_attempt,
                args.host,
                args.port,
                secret_lengths,
                attempt,
                args.attempts,
                args.verbose,
            )
            futures[future] = attempt

        while next_attempt <= args.attempts and len(futures) < args.workers:
            submit_attempt(next_attempt)
            next_attempt += 1

        while futures:
            done, _ = wait(futures, return_when=FIRST_COMPLETED)
            for future in done:
                attempt = futures.pop(future)
                try:
                    print(future.result())
                    for pending in futures:
                        pending.cancel()
                    return
                except Exception as exc:
                    last_error = exc
                    if args.verbose:
                        print(
                            f"[attempt {attempt}] failed: {exc!r}",
                            file=sys.stderr,
                            flush=True,
                        )
                    if next_attempt <= args.attempts:
                        submit_attempt(next_attempt)
                        next_attempt += 1

    raise SystemExit(str(last_error))


if __name__ == "__main__":
    main()
