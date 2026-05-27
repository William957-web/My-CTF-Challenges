from sage.all import *

import re
import subprocess


OUTPUT_PATH = "output.txt"
MAX_TRIES = 128
SMALL_FACTOR_LIMIT = 10**7
ECM_PLANS = (
    (50, 3_000_000),
    (100, 10_000_000),
)
FLAG_PREFIX = b"AIS3{"
KNOWN_TRIALS = (
    (59392, 50236, (12778, 27756, 17953, 28109)),
)
KNOWN_Q_FACTORS = (
    2,
    4001,
    109976715073,
)


def parse_output(path):
    vals = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "=" not in line:
                continue
            k, v = line.split("=", 1)
            vals[k.strip()] = Integer(v.strip())
    return vals["e"], vals["c"], vals["N*getPrime(512)"]


def int_to_bytes(value):
    value = Integer(value)
    if value == 0:
        return b"\x00"
    return value.to_bytes((value.nbits() + 7) // 8, "big")


def looks_like_flag(data):
    return (
        data.startswith(FLAG_PREFIX)
        and data.endswith(b"}")
        and all(32 <= b < 127 for b in data)
    )


def candidate_primes_from_divisor(divisor):
    for prime, _ in factor(divisor):
        prime = Integer(prime)
        if prime.is_prime():
            yield prime


def trial_params(tries):
    for b, c, coeffs_base in KNOWN_TRIALS:
        yield Integer(b), Integer(c), [Integer(v) for v in coeffs_base]
    for _ in range(tries):
        coeffs_base = [ZZ.random_element(0, 2**16) for _ in range(4)]
        if coeffs_base[1] == 0 and coeffs_base[3] == 0:
            coeffs_base[1] = 1
        yield (
            ZZ.random_element(0, 2**16),
            ZZ.random_element(1, 2**16),
            coeffs_base,
        )


def find_p(leaked, tries=MAX_TRIES):
    Zn = Integers(leaked)
    PR = PolynomialRing(Zn, "x")
    x = PR.gen()

    for attempt, (b, c, coeffs_base) in enumerate(trial_params(tries)):
        f = x**4 + b * x**2 + c

        try:
            Q = PR.quotient(f, "y")
        except Exception:
            continue

        y = Q.gen()

        base = sum(Zn(coeffs_base[i]) * y**i for i in range(4))
        value = base**leaked
        coeffs = value.lift().coefficients(sparse=False)
        coeffs += [Zn(0)] * (4 - len(coeffs))

        for idx in (1, 3):
            divisor = gcd(Integer(coeffs[idx]), leaked)
            if divisor in (0, 1, leaked):
                continue

            for cand in candidate_primes_from_divisor(divisor):
                if cand.nbits() < 400:
                    continue
                if leaked % (cand * (cand**2 + 1)) == 0:
                    print(f"[+] found p on attempt {attempt}, coeff {idx}")
                    return cand

    raise RuntimeError("failed to recover p")


def ecm_find_factor(n):
    n = Integer(n)
    for curves, b1 in ECM_PLANS:
        proc = subprocess.run(
            ["ecm", "-c", str(curves), str(b1)],
            input=f"{n}\n",
            text=True,
            capture_output=True,
            check=False,
        )
        text = proc.stdout + proc.stderr
        match = re.search(r"Found (?:prime|composite) factor of \d+ digits: (\d+)", text)
        if match:
            factor_ = Integer(match.group(1))
            if factor_ not in (1, n):
                return factor_
    return None


def yield_prime_factors(n):
    pending = [Integer(n)]

    while pending:
        current = pending.pop()
        if current == 1:
            continue
        if current.is_prime():
            yield current
            continue

        partial = factor(current, limit=SMALL_FACTOR_LIMIT)
        composite_parts = []

        for base, exp in partial:
            base = Integer(base)
            if base.is_prime():
                for _ in range(exp):
                    yield base
            else:
                composite_parts.extend([base] * exp)

        if not composite_parts:
            continue

        for comp in composite_parts:
            split = ecm_find_factor(comp)
            if split is None:
                print(f"[!] unable to split composite cofactor with {comp.nbits()} bits")
                continue
            pending.extend([comp // split, split])


def eth_root_mod_prime(c, e, prime):
    prime = Integer(prime)
    if prime == 2:
        return Integer(c % 2)
    d = inverse_mod(e, prime - 1)
    return power_mod(c, d, prime)


def recover_flag(e, c, p):
    q = p**2 + 1
    residues = [eth_root_mod_prime(c, e, p)]
    moduli = [p]
    remaining_q = Integer(q)

    print(f"[+] p = {p}")
    print(f"[+] q = p^2 + 1 = {q}")
    print(f"[+] starting CRT with modulus bits = {p.nbits()}")

    for factor_ in KNOWN_Q_FACTORS:
        factor_ = Integer(factor_)
        if remaining_q % factor_ != 0:
            continue
        remaining_q //= factor_
        phi_piece = 1 if factor_ == 2 else factor_ - 1
        if gcd(e, phi_piece) != 1:
            print(f"[-] skipping factor {factor_} since gcd(e, phi) != 1")
            continue

        residues.append(eth_root_mod_prime(c, e, factor_))
        moduli.append(factor_)

        modulus = prod(moduli)
        message = crt(residues, moduli)
        flag = int_to_bytes(message)

        print(f"[+] added factor {factor_} ({factor_.nbits()} bits), CRT modulus bits = {modulus.nbits()}")
        if looks_like_flag(flag):
            return flag, modulus

    for factor_ in yield_prime_factors(remaining_q):
        phi_piece = 1 if factor_ == 2 else factor_ - 1
        if gcd(e, phi_piece) != 1:
            print(f"[-] skipping factor {factor_} since gcd(e, phi) != 1")
            continue

        residues.append(eth_root_mod_prime(c, e, factor_))
        moduli.append(factor_)

        modulus = prod(moduli)
        message = crt(residues, moduli)
        flag = int_to_bytes(message)

        print(f"[+] added factor {factor_} ({factor_.nbits()} bits), CRT modulus bits = {modulus.nbits()}")
        if looks_like_flag(flag):
            return flag, modulus

    message = crt(residues, moduli)
    return int_to_bytes(message), prod(moduli)


def main():
    e, c, leaked = parse_output(OUTPUT_PATH)
    print(f"[*] loaded output: e bits={e.nbits()}, c bits={c.nbits()}, leaked bits={leaked.nbits()}")

    p = find_p(leaked)
    flag, modulus = recover_flag(e, c, p)

    print(f"[+] recovered modulus bits = {modulus.nbits()}")
    print(f"[+] flag = {flag.decode()}")


if __name__ == "__main__":
    main()
