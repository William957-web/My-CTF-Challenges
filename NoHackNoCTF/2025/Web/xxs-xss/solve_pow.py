import hashlib
import sys

PREFIX = "000000"

def solve_pow(challenge):
    for i in range(10000000000):
        nonce = str(i)
        combined = challenge + nonce
        h = hashlib.sha256(combined.encode()).hexdigest()
        if h.startswith(PREFIX):
            print(f"[+] Challenge: {challenge}")
            print(f"[+] Found nonce: {nonce}")
            print(f"[+] Hash: {h}")
            return
    print("[-] Failed to find a valid nonce")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <challenge>")
        sys.exit(1)

    challenge = sys.argv[1]
    solve_pow(challenge)
