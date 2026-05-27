import hashlib
import struct
from re import findall
from subprocess import check_output

Q = 127707000586261266406140258152342164811114836442218367658989756920303451547391
P = 257
DIM = 512
ENC_MAGIC = b"BDRW"
STR_A_TO_Z = "abcdefghijklmnopqrstuvwxyz_0OABCDEFG"
KNOWN = {
    0: ord("A"),
    1: ord("I"),
    2: ord("S"),
    3: ord("3"),
    4: ord("{"),
    5: ord("w"),
}


def flatter(M):
    M = matrix(ZZ, M)
    z = "[[" + "]\n[".join(" ".join(map(str, row)) for row in M.rows()) + "]]"
    ret = check_output(["flatter"], input=z.encode())
    return matrix(M.nrows(), M.ncols(), map(int, findall(b"-?\\d+", ret)))


def load_blob(path):
    blob = open(path, "rb").read()
    if blob[:4] != ENC_MAGIC:
        raise ValueError("invalid enc.bin magic")
    ciphertext_len = struct.unpack(">I", blob[4:8])[0]
    ciphertext = blob[8 : 8 + ciphertext_len]
    offset = 8 + ciphertext_len
    value_bytes = (Q.bit_length() + 7) // 8
    lwe = [
        int.from_bytes(blob[offset + i * value_bytes : offset + (i + 1) * value_bytes], "big")
        for i in range(DIM)
    ]
    return ciphertext, lwe


def recover_key_byte(value):
    x_weight = 1000
    target_weight = 10^30
    rows = []
    for k, h in enumerate(hashes):
        row = [0] * (len(hashes) + 2)
        row[k] = x_weight
        row[-1] = h
        rows.append(row)
    rows.append([0] * (len(hashes) + 1) + [Q])
    rows.append([0] * len(hashes) + [target_weight, -value])

    reduced = flatter(rows)
    for row in reduced:
        if abs(row[-2]) != target_weight:
            continue
        sign = 1 if row[-2] == target_weight else -1
        epsilon = -(row[-1] * sign)
        if epsilon < 0:
            continue
        return int(epsilon % P)
    raise ValueError("normal recovery failed")


ciphertext, lwe = load_blob("enc.bin")
hashes = [
    int.from_bytes(hashlib.sha256(char.encode()).digest(), "big")
    for char in STR_A_TO_Z
]

flag = []
for i, value in enumerate(lwe):
    if i in KNOWN:
        flag.append(KNOWN[i])
    else:
        key = recover_key_byte(value)
        if i == 0:
            stream = key
        else:
            stream = (key * flag[i - 1]) & 0xff
        flag.append(ciphertext[i] ^^ stream)

print(bytes(flag).decode())
