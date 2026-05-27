import base64
import hashlib

N = 528302026814581112698976132408136607344677298272713726039361987095410824358231139478581273

def load_flag(path="/flag.txt"):
    with open(path, "rb") as fh:
        return fh.read().strip()


def decode_suffix(data):
    return base64.urlsafe_b64decode(data.encode())


def encode_suffix(raw):
    return base64.urlsafe_b64encode(raw).decode()


def hash_suffix(flag, suffix):
    return hashlib.sha256(flag + suffix).digest()


def flip_digest_bit(digest, index):
    if not 0 <= index < 256:
        raise ValueError("bit index out of range")
    mutated = bytearray(digest)
    byte_index, bit_index = divmod(index, 8)
    mutated[byte_index] ^= 1 << (7 - bit_index)
    return bytes(mutated)


def compute_proof_from_digest(digest, seed):
    value = 0
    for byte in digest:
        for offset in range(7, -1, -1):
            if (byte >> offset) & 1 == 0:
                raw_value = value + seed
                value = raw_value % N
            else:
                value = pow(value, seed, N)
    return value


def compute_proof(flag, suffix, seed, bit_flip_indices=None):
    digest = hash_suffix(flag, suffix)
    if bit_flip_indices is not None:
        for index in bit_flip_indices:
            digest = flip_digest_bit(digest, index)
    return compute_proof_from_digest(digest, seed)
