from sage.all import *
from Crypto.Cipher import AES
import hashlib

# --- 1. 環境設定 ---
ea, eb = 13, 7
p = 2**ea * 3**eb - 1
K.<i> = GF(p**2, modulus=x**2 + 1)
R.<y> = PolynomialRing(K)


# Output~
'''
E0: (0, 6, 0, 1, 0)
Eab: (0, 6, 0, 11067381*i + 1118198, 8021433*i + 1906048)
P_pub: (8959148*i + 2448181, 10026959*i + 706144)
ciphertext: 1aca81de78c79d95adc0b14f4dfb3c8121f900896c4ddd05fba6070f12f9a5ce94782503d5f8343ea8d237ea1eb13e76464a88cd4992fcad27e11af22b3fcd1a
'''
E0_inv = (0, 6, 0, 1, 0)
Eab_inv = (0, 6, 0, 11067381*i + 1118198, 8021433*i + 1906048)
P_pub_coords = (8959148*i + 2448181, 10026959*i + 706144)
ciphertext_hex = "1aca81de78c79d95adc0b14f4dfb3c8121f900896c4ddd05fba6070f12f9a5ce94782503d5f8343ea8d237ea1eb13e76464a88cd4992fcad27e11af22b3fcd1a"

E0 = EllipticCurve(K, E0_inv)
Eab = EllipticCurve(K, Eab_inv)
P_pub = E0(P_pub_coords)

Phi2 = classical_modular_polynomial(2)
Phi3 = classical_modular_polynomial(3)

def get_all_next_js(Phi, jc):
    """允許回頭路，獲取所有鄰居"""
    f = Phi(jc, y)
    return [r for r, _ in f.roots()]

# --- 2. 精確深度搜尋 (允許回頭路) ---
def build_full_tree(start_j, Phi, depth):
    # tree[d][curr_j] = [prev_js]
    tree = {d: {} for d in range(depth + 1)}
    tree[0][start_j] = [None]
    
    curr_nodes = [start_j]
    for d in range(depth):
        next_nodes = []
        for jc in curr_nodes:
            neighbors = get_all_next_js(Phi, jc)
            for jn in neighbors:
                if jn not in tree[d+1]:
                    tree[d+1][jn] = []
                    next_nodes.append(jn)
                tree[d+1][jn].append(jc)
        curr_nodes = next_nodes
    return tree

print(f"[*] 正在執行全路徑搜尋 (允許回頭路, ea={ea}, eb={eb})...")
tree_a = build_full_tree(E0.j_invariant(), Phi2, ea)
tree_b = build_full_tree(Eab.j_invariant(), Phi3, eb)

intersections = set(tree_a[ea].keys()) & set(tree_b[eb].keys())
print(f"[*] 發現 {len(intersections)} 個在精確深度重合的交點")

# --- 3. 路徑還原 ---
def get_paths_recursive(tree, depth, curr_j):
    if depth == 0:
        return [[curr_j]]
    all_p = []
    for prev_j in tree[depth][curr_j]:
        for p in get_paths_recursive(tree, depth - 1, prev_j):
            all_p.append(p + [curr_j])
    return all_p

def push_point_exhaustive(P, j_path, l):
    candidates = [P]
    for k in range(len(j_path) - 1):
        target_j = j_path[k+1]
        next_gen = []
        for p in candidates:
            for phi in p.curve().isogenies_prime_degree(l):
                if phi.codomain().j_invariant() == target_j:
                    next_gen.append(phi(p))
        # 依據座標去重，但必須保留正負 y 的可能性
        unique = {pt.xy(): pt for pt in next_gen}
        candidates = list(unique.values())
    return candidates

# --- 4. 爆破解密 ---
ct_bytes = bytes.fromhex(ciphertext_hex)
iv, ct = ct_bytes[:16], ct_bytes[16:]

for j_int in intersections:
    print(f"[*] 嘗試交點 {j_int}...")
    paths_a = get_paths_recursive(tree_a, ea, j_int)
    paths_b_rev = get_paths_recursive(tree_b, eb, j_int)
    
    for pa in paths_a:
        pts_ea = push_point_exhaustive(P_pub, pa, 2)
        for pb_from_eab in paths_b_rev:
            pb = pb_from_eab[::-1] # 反轉成 Ea -> Eab
            for p_ea in pts_ea:
                pts_final = push_point_exhaustive(p_ea, pb, 3)
                for pf in pts_final:
                    # 同構修正
                    iso = pf.curve().isomorphism_to(Eab)
                    p_correct = iso(pf)
                    
                    # 測試 P 與 -P
                    for cand in [p_correct, -p_correct]:
                        sx = cand.xy()[0]
                        # 嚴格模擬 chal.sage 的序列化格式
                        key = hashlib.sha256(str(sx).encode()).digest()[:16]
                        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
                        dec = cipher.decrypt(ct)
                        
                        if b"THJCC" in dec:
                            print(f"\n[!] 成功！")
                            print(f"Flag: {dec[:-dec[-1]].decode()}")
                            exit()