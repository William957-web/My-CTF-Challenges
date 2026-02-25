from sage.all import *
from Crypto.Cipher import AES
import hashlib

# --- 1. 環境設定 ---
p = 2**13 * 3**12 - 1
K.<i> = GF(p**2, modulus=x**2 + 1)

# 題目給出的數據
E0 = EllipticCurve(K, [0, 6, 0, 1, 0])
Eab = EllipticCurve(K, [0, 6, 0, 3680293486*i + 2460298332, 354978262*i + 2386920523])
P_pub_coords = (11478215*i + 1670704458, 2331172596*i + 670189971)
P_pub = E0(P_pub_coords)

ciphertext_hex = "8c3e75c9da4820628faf5edb0568a76784866f833fd7052cf1715827cf15c3605aee69b1ddc8c51c3a674567b68f6084b0ea5cb0d28bdaaedb8966a312596ee8"
ct_bytes = bytes.fromhex(ciphertext_hex)
iv = ct_bytes[:16]
encrypted_flag = ct_bytes[16:]

# --- 2. 定義路徑搜尋函式 ---
def build_isogeny_tree(start_E, l, depth):
    """
    使用 BFS 遍歷同源圖
    回傳字典 { j_invariant: [phis_list] }
    """
    tree = {start_E.j_invariant(): []}
    queue = [(start_E, [])]
    
    for _ in range(depth):
        next_queue = []
        for curr_E, path in queue:
            # 尋找所有度數為 l 的同源映射
            # 排除掉回頭的路徑 (dual isogeny)
            for phi in curr_E.isogenies_prime_degree(l):
                target_E = phi.codomain()
                target_j = target_E.j_invariant()
                if target_j not in tree:
                    new_path = path + [phi]
                    tree[target_j] = new_path
                    next_queue.append((target_E, new_path))
        queue = next_queue
        # print(f"Depth {_ + 1} finished, found {len(tree)} nodes")
    return tree

# --- 3. 執行中途相遇攻擊 ---
print("[*] 正在搜尋從 E0 出發的 2^13 同源路徑...")
# 2^13 的搜尋空間很小 (約 1.2 萬個節點)
tree_a = build_isogeny_tree(E0, 2, 13)

print("[*] 正在搜尋從 Eab 出發的 3^12 同源路徑...")
# 3^12 的搜尋空間稍大 (約 70 萬個節點)，需要一點時間
tree_b = build_isogeny_tree(Eab, 3, 12)

# --- 4. 尋找交點 Ea ---
target_j = None
for j in tree_a:
    if j in tree_b:
        target_j = j
        break

if target_j:
    print(f"[+] 找到中間曲線 Ea! j-inv: {target_j}")
    
    # 第一段映射：E0 -> Ea
    phi_a_list = tree_a[target_j]
    P_intermediate = P_pub
    for phi in phi_a_list:
        P_intermediate = phi(P_intermediate)
    
    # 第二段映射：Ea -> Eab
    # 注意：tree_b 存的是 Eab -> Ea 的路徑，我們需要的是其反向
    # 最簡單的方法是從現在的 P_intermediate (在 Ea 上) 重新搜尋到 Eab 的 3-isogeny 路徑
    Ea = P_intermediate.curve()
    print("[*] 正在重新建構 Ea 到 Eab 的最終映射...")
    tree_final = build_isogeny_tree(Ea, 3, 12)
    phi_b_list = tree_final[Eab.j_invariant()]
    
    P_priv = P_intermediate
    for phi in phi_b_list:
        P_priv = phi(P_priv)
    
    # --- 5. 解密 ---
    shared_x = P_priv.xy()[0]
    key = hashlib.sha256(str(shared_x).encode()).digest()[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    
    decrypted = cipher.decrypt(encrypted_flag)
    # 去除 PKCS7 padding
    pad_len = decrypted[-1]
    flag = decrypted[:-pad_len]
    print(f"\n[!] 成功取得 Flag: {flag.decode()}")
else:
    print("[-] 失敗：找不到交會點，請確認參數是否正確。")