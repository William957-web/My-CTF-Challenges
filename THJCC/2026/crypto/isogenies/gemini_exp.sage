from sage.all import *
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib

# 1. 初始化參數
ea, eb = 13, 7
p = 2**ea * 3**eb - 1
K.<i> = GF(p**2, modulus=x**2 + 1)

E0 = EllipticCurve(K, [0, 6, 0, 1, 0])
# 題目給的 Eab invariants
Eab_inv = (0, 6, 0, 11067381*i + 1118198, 8021433*i + 1906048)
Eab_target = EllipticCurve(K, list(Eab_inv))
target_j = Eab_target.j_invariant()

P_pub = E0(8959148*i + 2448181, 10026959*i + 706144)
ciphertext = bytes.fromhex("1aca81de78c79d95adc0b14f4dfb3c8121f900896c4ddd05fba6070f12f9a5ce94782503d5f8343ea8d237ea1eb13e76464a88cd4992fcad27e11af22b3fcd1a")

def get_isogeny_chain(E, l, e, secret):
    curr_E = E
    phis = []
    for j in range(e):
        P, Q = curr_E.torsion_basis(l**(e-j))
        kernel_pt = (P + secret * Q) * l**(e-j-1)
        phi = curr_E.isogeny(kernel_pt)
        phis.append(phi)
        curr_E = phi.codomain()
    return curr_E, phis

def push_point(phi_list, P):
    curr_P = P
    for phi in phi_list:
        curr_P = phi(curr_P)
    return curr_P

# 2. 爆破 sa 並儲存 Ea 的 j-invariant
print("[*] Searching for sa and sb...")
found = False
for sa in range(2**ea):
    Ea, phis_a = get_isogeny_chain(E0, 2, ea, sa)
    # 對於每一個 Ea，檢查是否能透過 sb 到達目標 Eab
    # 這裡使用內層循環，因為 sb 空間很小 (2187)
    for sb in range(3**eb):
        Eab_test, phis_b = get_isogeny_chain(Ea, 3, eb, sb)
        if Eab_test.j_invariant() == target_j:
            # 進一步確認 a-invariants 是否完全匹配
            if Eab_test.a_invariants() == Eab_inv:
                print(f"[+] Found! sa: {sa}, sb: {sb}")
                
                # 3. 計算共享點 P_priv
                P_priv = push_point(phis_b, push_point(phis_a, P_pub))
                shared_x = P_priv.xy()[0]
                
                # 4. 解密 Flag
                key = hashlib.sha256(str(shared_x).encode()).digest()[:16]
                iv = ciphertext[:16]
                ct = ciphertext[16:]
                cipher = AES.new(key, AES.MODE_CBC, iv=iv)
                flag = unpad(cipher.decrypt(ct), 16)
                print(f"[!] Flag: {flag.decode()}")
                found = True
                break
    if found: break
    if sa % 500 == 0: print(f"Progress: sa={sa}...")
