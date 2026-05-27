#!/usr/bin/env python3
import argparse
import socket
import subprocess
import sys
from dataclasses import dataclass


N = 528302026814581112698976132408136607344677298272713726039361987095410824358231139478581273
p = 725150593990274719678916870531826926518549387
q = 728541121241453991456684214253885334575843179
s = 5175996367017249359
probe_salt = 3


def is_s_residue_mod_p(x: int) -> bool:
    x %= p
    return x == 0 or pow(x, (p - 1) // s, p) == 1


class Tube:
    def recv_until(self, marker: bytes) -> bytes:
        raise NotImplementedError

    def send_line(self, line: str) -> None:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError


class SocketTube(Tube):
    def __init__(self, host: str, port: int):
        self.sock = socket.create_connection((host, port))
        self.buf = b""

    def recv_until(self, marker: bytes) -> bytes:
        while marker not in self.buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise EOFError(f"connection closed while waiting for {marker!r}")
            self.buf += chunk
        idx = self.buf.index(marker) + len(marker)
        out = self.buf[:idx]
        self.buf = self.buf[idx:]
        return out

    def send_line(self, line: str) -> None:
        self.sock.sendall(line.encode() + b"\n")

    def close(self) -> None:
        self.sock.close()


class ProcessTube(Tube):
    def __init__(self, argv: list[str]):
        self.proc = subprocess.Popen(
            argv,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        self.buf = b""

    def recv_until(self, marker: bytes) -> bytes:
        assert self.proc.stdout is not None
        while marker not in self.buf:
            chunk = self.proc.stdout.read(1)
            if not chunk:
                raise EOFError(f"process closed while waiting for {marker!r}")
            self.buf += chunk
        idx = self.buf.index(marker) + len(marker)
        out = self.buf[:idx]
        self.buf = self.buf[idx:]
        return out

    def send_line(self, line: str) -> None:
        assert self.proc.stdin is not None
        self.proc.stdin.write(line.encode() + b"\n")
        self.proc.stdin.flush()

    def close(self) -> None:
        if self.proc.poll() is None:
            self.proc.kill()
        self.proc.wait()


@dataclass
class Solver:
    tube: Tube
    bits: int
    verbose: bool = False
    used_guess: int = 0
    used_adjust: int = 0

    def log(self, msg: str) -> None:
        if self.verbose:
            print(msg, file=sys.stderr)

    def oracle(self) -> int:
        self.tube.recv_until(b"option? ")
        self.tube.send_line("1")
        self.tube.recv_until(b"salt? ")
        self.tube.send_line(str(s))
        line = self.tube.recv_until(b"\n").strip()
        value = int(line)
        self.used_guess += 1
        self.log(f"oracle -> {value}")
        return value

    def adjust(self, bit: int) -> None:
        self.tube.recv_until(b"option? ")
        self.tube.send_line("2")
        self.tube.recv_until(b"salt? ")
        self.tube.send_line(str(1 << bit))
        self.used_adjust += 1
        self.log(f"adjust bit {bit}")

    def guess(self, ans: int) -> str:
        self.tube.recv_until(b"guess? ")
        self.tube.send_line(str(ans))
        out = self.tube.recv_until(b"\n").decode().strip()
        return out

    def burn_remaining(self) -> None:
        while self.used_guess < 128:
            self.tube.recv_until(b"option? ")
            self.tube.send_line("1")
            self.tube.recv_until(b"salt? ")
            self.tube.send_line("2")
            self.tube.recv_until(b"\n")
            self.used_guess += 1
        while self.used_adjust < 128:
            self.tube.recv_until(b"option? ")
            self.tube.send_line("2")
            self.tube.recv_until(b"salt? ")
            self.tube.send_line("1")
            self.used_adjust += 1

    def solve(self) -> int:
        self.tube.recv_until(b"option? ")
        recovered_low = 0
        run_low = None
        while True:
            if self.used_guess >= 128:
                raise RuntimeError("guess budget exhausted before recovery finished")
            self.tube.send_line("1")
            self.tube.recv_until(b"salt? ")
            self.tube.send_line(str(s))
            y = int(self.tube.recv_until(b"\n").strip())
            self.used_guess += 1

            hit = None
            for k in range(self.bits):
                z = y - k * s
                if is_s_residue_mod_p(z):
                    hit = (k, z)
                    break
            if hit is None:
                raise RuntimeError("no residue hit found in expected range")

            bit, z = hit
            recovered_low |= 1 << bit
            self.log(f"found bit {bit}, z={z}")

            if z == 0:
                run_low = bit
                break

            self.tube.recv_until(b"option? ")
            self.tube.send_line("2")
            self.tube.recv_until(b"salt? ")
            self.tube.send_line(str(1 << bit))
            self.used_adjust += 1

        assert run_low is not None

        # Once z == 0, the remaining token is exactly ((1 << r) - 1) << run_low.
        candidates = [((1 << r) - 1) << run_low for r in range(1, self.bits - run_low + 1)]
        probe_bit = self.bits

        if self.used_adjust >= 128 or self.used_guess >= 128:
            raise RuntimeError("not enough budget left for final probe")
        self.tube.recv_until(b"option? ")
        self.tube.send_line("2")
        self.tube.recv_until(b"salt? ")
        self.tube.send_line(str(1 << probe_bit))
        self.used_adjust += 1

        self.tube.recv_until(b"option? ")
        self.tube.send_line("1")
        self.tube.recv_until(b"salt? ")
        self.tube.send_line(str(probe_salt))
        probe_value = int(self.tube.recv_until(b"\n").strip())
        self.used_guess += 1

        self.tube.recv_until(b"option? ")
        self.tube.send_line("2")
        self.tube.recv_until(b"salt? ")
        self.tube.send_line(str(1 << probe_bit))
        self.used_adjust += 1

        matches = [
            cand
            for cand in candidates
            if oracle_local(cand ^ (1 << probe_bit), probe_salt) == probe_value
        ]
        if len(matches) != 1:
            raise RuntimeError(f"candidate identification failed: {len(matches)} matches")

        remaining = matches[0]
        self.log(f"remaining run = {remaining:b}")
        return recovered_low | remaining


def oracle_local(trial: int, salt: int) -> int:
    cnt = 0
    for c in bin(trial)[2:]:
        if c == "0":
            cnt += salt
        else:
            cnt = pow(cnt, salt, N)
    return cnt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--bits", type=int, default=256)
    parser.add_argument("--attempts", type=int, default=1)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    if not args.local and not (args.host and args.port):
        parser.error("use --local or --host/--port")

    last_error = None
    for attempt in range(1, args.attempts + 1):
        if args.local:
            tube: Tube = ProcessTube(
                ["python3", "/home/whale/ctf/pre-exam/2026/crypto/babyoracle/dist/share/chal.py"]
            )
        else:
            tube = SocketTube(args.host, args.port)

        solver = Solver(tube=tube, bits=args.bits, verbose=args.verbose)
        try:
            ans = solver.solve()
            solver.burn_remaining()
            result = solver.guess(ans)
            print(ans)
            print(result)
            if result != "awa":
                return
            last_error = RuntimeError("solver completed but guess was rejected")
        except Exception as exc:
            last_error = exc
            if args.verbose:
                print(f"attempt {attempt} failed: {exc}", file=sys.stderr)
        finally:
            tube.close()

    raise SystemExit(str(last_error))


if __name__ == "__main__":
    main()
