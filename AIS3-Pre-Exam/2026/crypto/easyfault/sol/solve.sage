from sage.all import *
import ast
from hashlib import shake_256
from multiprocessing import Pool, cpu_count
from operator import xor
import os
from re import findall
from subprocess import check_output
from time import perf_counter

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(it=None, **kwargs):
        return it if it is not None else None


solve_count = 0
BITS = 448
AUX_BITS = 32
AUX_ROUNDS = 72
KEYBITS = 192
WORKERS = max(1, min(32, cpu_count() or 1))

MOD_SAMPLES = None


def flatter(M):
    M = matrix(ZZ, M)
    z = "[[" + "]\n[".join(" ".join(map(str, row)) for row in M.rows()) + "]]"
    ret = check_output(["flatter"], input=z.encode())
    return matrix(M.nrows(), M.ncols(), map(int, findall(b"-?\\d+", ret)))


def reduce_lattice(M):
    return flatter(matrix(ZZ, M))


def parse(path):
    tree = ast.parse(open(path).read(), path, "exec")
    values = {}
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
            values[stmt.targets[0].id] = ast.literal_eval(stmt.value)
    return values["blob"], values["data"]


def relation_weight(row):
    return sum(abs(int(v)) for v in row)


def kernel_basis(vals, bias, mod, rounds):
    base = matrix(GF(mod), [vals, bias]).echelon_form()
    pivots = base.pivots()
    free = [j for j in range(rounds) if j not in pivots]
    rows = []
    for col in free:
        row = [0] * rounds
        row[col] = 1
        for i, pivot in enumerate(pivots):
            row[pivot] = int(-base[i, col])
        rows.append(row)
    for pivot in pivots:
        row = [0] * rounds
        row[pivot] = mod
        rows.append(row)
    return matrix(ZZ, rows)


def recover_total(mod, bias, vals, bits, rounds):
    lat = reduce_lattice(kernel_basis(vals, bias, mod, rounds))
    rows = sorted(lat.rows(), key=lambda row: row.norm())
    short = matrix(ZZ, [list(row) for row in rows[: rounds - bits - 1]])
    return reduce_lattice(short.right_kernel_matrix())


def aux_relation_lattice(basis):
    return reduce_lattice(matrix(ZZ, [list(row) for row in basis.rows()]).right_kernel_matrix())


def recover_key(pack):
    totals = []
    for item in tqdm(pack, desc="aux lattices"):
        totals.append(recover_total(*item, AUX_BITS, AUX_ROUNDS))
    lat = totals[0].row_module(ZZ)
    for item in tqdm(totals[1:], desc="aux intersect", leave=False):
        lat = lat.intersection(item.row_module(ZZ))
    basis = reduce_lattice(lat.basis_matrix())
    if basis.rank() != AUX_BITS:
        raise ValueError("failed to recover auxiliary lattice")
    rel = aux_relation_lattice(basis)
    for row in tqdm(sorted(rel.rows(), key=relation_weight), desc="aux key search", leave=False):
        coeffs = [ZZ(v) for v in row]
        keys = []
        ok = True
        for mod, bias, vals in pack:
            denom = sum(c * b for c, b in zip(coeffs, bias)) % mod
            if denom == 0:
                ok = False
                break
            numer = sum(c * v for c, v in zip(coeffs, vals)) % mod
            keys.append(int((-numer) * inverse_mod(denom, mod) % mod))
        if ok and len(set(keys)) == 1:
            return keys[0]
    raise ValueError("failed to recover key")


def mix(key, idx):
    buf = shake_256(key.to_bytes(KEYBITS // 8, "big") + idx.to_bytes(4, "big")).digest(BITS // 8)
    return int.from_bytes(buf, "big")


def unmask(data, key):
    return [(xor(masked, mix(key, i)), value) for i, (masked, value) in enumerate(data)]


def bitvec(x):
    return [(x >> i) & 1 for i in range(BITS)]


def row_head_zero(row, size):
    return all(v == 0 for v in row[:size])


def init_mod_workers(samples):
    global MOD_SAMPLES
    MOD_SAMPLES = samples


def modulus_relation_delta(coeffs):
    global solve_count
    print(f"[+] Log: new modulus_relation_delta!")
    lhs = ZZ(1)
    rhs = ZZ(1)
    for value, coef in zip(MOD_SAMPLES, coeffs):
        if coef > 0:
            lhs *= ZZ(value) ** int(coef)
        elif coef < 0:
            rhs *= ZZ(value) ** int(-coef)
    solve_count += 1
    print(f"[+] Log: solved {solve_count} modulus")
    return lhs - rhs


def recover_modulus(data):
    mat = matrix(ZZ, [bitvec(fault) + [1] for fault, _ in data])
    lat = mat.augment(identity_matrix(ZZ, len(data)))
    for i in range(BITS + 1):
        lat.rescale_col(i, 2**64)
    print("[+] Log: lattice going to reduce")
    lat = reduce_lattice(lat)
    print("[+] Log: lattice finished reduced")
    rows = []
    for row in lat.rows():
        if not row_head_zero(row, BITS + 1):
            continue
        coeffs = [ZZ(v) for v in row[BITS + 1 :]]
        weight = sum(abs(v) for v in coeffs)
        if weight == 0:
            continue
        rows.append((weight, coeffs))
    rows.sort(key=lambda item: item[0])
    coeff_rows = [coeffs for _, coeffs in rows[:BITS]]
    samples = [int(value) for _, value in data]
    print("[+] Log: going to workers!")
    n = ZZ(0)
    workers = int(os.getenv("EASYFAULT_WORKERS", str(WORKERS)))
    chunksize = max(1, len(coeff_rows) // max(1, workers * 4))
    with Pool(workers, initializer=init_mod_workers, initargs=(samples,)) as pool:
        it = pool.imap_unordered(modulus_relation_delta, coeff_rows, chunksize)
        for delta in tqdm(it, total=len(coeff_rows), desc=f"modulus relations x{workers}"):
            n = gcd(n, delta)
    if n == 0:
        raise ValueError("failed to recover modulus")
    for prime in prime_range(10**4):
        while n % prime == 0:
            n //= prime
    changed = True
    while changed:
        changed = False
        for _, sample in data:
            common = gcd(n, ZZ(sample))
            if 1 < common < n:
                n //= common
                changed = True
    return int(n)


def recover_relation_rows(data):
    mat = matrix(ZZ, [bitvec(fault) + [1] for fault, _ in data])
    lat = mat.augment(identity_matrix(ZZ, len(data)))
    for i in range(BITS):
        lat.rescale_col(i, 2**64)
    lat.rescale_col(BITS, 8)
    lat = reduce_lattice(lat).change_ring(QQ)
    lat.rescale_col(BITS, QQ(1) / 8)
    lat = lat.change_ring(ZZ)

    rows = []
    for row in tqdm(lat.rows(), desc="message relations"):
        if not row_head_zero(row, BITS):
            continue
        power = ZZ(row[BITS])
        if power == 0:
            continue
        coeffs = [ZZ(v) for v in row[BITS + 1 :]]
        if power < 0:
            power = -power
            coeffs = [-v for v in coeffs]
        weight = abs(power) + sum(abs(v) for v in coeffs)
        rows.append((weight, power, coeffs))
    rows.sort(key=lambda item: item[0])
    return [(power, coeffs) for _, power, coeffs in rows[: 2 * BITS]]


def combine_relations(rows, size):
    power = ZZ(0)
    coeffs = [ZZ(0)] * size
    for nxt_power, nxt_coeffs in tqdm(rows, desc="power combine", leave=False):
        if power == 0:
            power = nxt_power
            coeffs = list(nxt_coeffs)
        else:
            g, a, b = xgcd(power, nxt_power)
            coeffs = [a * u + b * v for u, v in zip(coeffs, nxt_coeffs)]
            power = g
        if power == 1:
            return coeffs
    raise ValueError("failed to isolate plaintext power")


def eval_relation(coeffs, data, n):
    value = Mod(1, n)
    for (_, sample), coef in zip(data, coeffs):
        coef = int(coef)
        if coef > 0:
            value *= power_mod(sample, coef, n)
        elif coef < 0:
            value *= power_mod(inverse_mod(sample, n), -coef, n)
    return int(value)


tick = perf_counter()
steps = tqdm(total=int(5), desc="solve", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]")

pack, data = parse("output.txt")
steps.update()

key = recover_key(pack)
steps.update()

data = unmask(data, key)
n = recover_modulus(data)
steps.update()

rows = recover_relation_rows(data)
steps.update()

msg = eval_relation(combine_relations(rows, len(data)), data, n)
steps.update()
steps.close()
print(f"[+] solved in {perf_counter() - tick:.2f}s")
print(Integer(msg).to_bytes((msg.bit_length() + 7) // 8, "big").decode())
