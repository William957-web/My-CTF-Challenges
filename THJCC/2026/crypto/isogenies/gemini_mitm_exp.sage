from sage.all import *
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# 1. 設置環境與題目數據
ea, eb = 13, 7
p = 2**ea * 3**eb - 1
R.<x> = PolynomialRing(GF(p))
K.<i> = GF(p**2, modulus=x**2 + 1)

E0 = EllipticCurve(K, [0, 6, 0, 1, 0])
# 題目提供的目標曲線
target_a_inv = (0, 6, 0, 11067381*i + 1118198, 8021433*i + 1906048)
Eab_target = EllipticCurve(K, list(target_a_inv))
target_j = Eab_target.j_invariant()

P_pub = E0(8959148*i + 2448181, 10026959*i + 706144)
ciphertext = bytes.fromhex("1aca81de78c79d95adc0b14f4dfb3c8121f900896c4ddd05fba6070f12f9a5ce94782503d5f8343ea8d237ea1eb13e76464a88cd4992fcad27e11af22b3fcd1a")

# 2. MitM 搜尋 (正向 Alice, 逆向 Bob)
print("[*] Walking Alice's tree...")
alice_nodes = {E0.j_invariant(): []}
queue = [(E0, [])]
for _ in range(ea):
    new_queue = []
    for E_curr, phis in queue:
        prev_j = phis[-1].domain().j_invariant() if phis else None
        for phi in E_curr.isogenies_prime_degree(2):
            E_next = phi.codomain()
            j_next = E_next.j_invariant()
            if j_next == prev_j: continue
            if j_next not in alice_nodes:
                alice_nodes[j_next] = phis + [phi]
                new_queue.append((E_next, phis + [phi]))
    queue = new_queue

print("[*] Walking Bob's tree backward...")
intersection_j = None
bob_backward_phis = []
queue = [(Eab_target, [])]
for _ in range(eb):
    new_queue = []
    for E_curr, phis in queue:
        prev_j = phis[-1].domain().j_invariant() if phis else None
        for phi in E_curr.isogenies_prime_degree(3):
            E_next = phi.codomain()
            j_next = E_next.j_invariant()
            if j_next == prev_j: continue
            if j_next in alice_nodes:
                intersection_j = j_next
                bob_backward_phis = phis + [phi]
                break
            new_queue.append((E_next, phis + [phi]))
        if intersection_j: break
    if intersection_j: break
    queue = new_queue

# 3. 重構點並修正同構
if intersection_j:
    print(f"[+] Found Bridge at j = {intersection_j}")
    phis_a = alice_nodes[intersection_j]
    Ea = phis_a[-1].codomain() if phis_a else E0
    
    # 重構 Bob 的正向路徑
    print("[*] Reconstructing Bob's forward path...")
    # bob_backward_phis 是 Eab -> ... -> Ea
    target_path_js = [p.domain().j_invariant() for p in bob_backward_phis][::-1] + [target_j]
    curr_E = Ea
    phis_b = []
    for nxt_j in target_path_js[1:]:
        for phi in curr_E.isogenies_prime_degree(3):
            if phi.codomain().j_invariant() == nxt_j:
                phis_b.append(phi)
                curr_E = phi.codomain()
                break
    
    # 推導點
    print("[*] Pushing points...")
    P_tmp = P_pub
    for phi in phis_a: P_tmp = phi(P_tmp)
    for phi in phis_b: P_tmp = phi(P_tmp)
    
    # 核心修正：處理同構
    # P_tmp 目前在 curr_E 上，但我們需要它在 Eab_target 上
    print("[*] Applying isomorphism correction...")
    iso = curr_E.isomorphism_to(Eab_target)
    P_priv = iso(P_tmp)
    
    # 這裡還有一個小細節：str(shared_x) 可能因為 y 的正負號而不同 (y 或 -y)
    # 但 x 座標在同構下通常是唯一的（除非 j=0, 1728，但這裡不是）
    shared_x = P_priv.xy()[0]
    
    # 嘗試解密
    key = hashlib.sha256(str(shared_x).encode()).digest()[:16]
    iv, ct = ciphertext[:16], ciphertext[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    
    try:
        flag = unpad(cipher.decrypt(ct), 16)
        print("\n" + "="*40)
        print(f"FLAG: {flag.decode()}")
        print("="*40)
    except:
        # 如果失敗，嘗試 y 的對偶（雖然 x 相同，但這能排除萬一）
        print("[!] Trying negate y...")
        P_neg = Eab_target(shared_x, -P_priv.xy()[1])
        # 事實上 x 座標在 (x, y) 和 (x, -y) 是一樣的，所以 str(shared_x) 不會變
        # 如果還是錯，代表 str() 的輸出格式與題目環境不一致
        print("[X] Still failed. Check Sage field representation.")