from sage.all import *
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Util.number import long_to_bytes

def solve():
    print("[*] Loading data and recovering p...")
    with open('output.json', 'r') as f:
        data = json.load(f)
    
    M_zz = matrix(ZZ, data['M'])
    C_zz = matrix(ZZ, data['C'])
    enc_flag = bytes.fromhex(data['enc'])
    
    # 透過 GCD 還原 p
    diff = M_zz * C_zz - C_zz * M_zz
    p_val = 0
    for x in diff.list():
        p_val = gcd(p_val, int(x))
    print(f"[+] Recovered p: {p_val.bit_length()} bits")

    results = []
    moduli = []

    def collect_dlog_info(char):
        print(f"[*] Processing Channel GF({char})...")
        F = GF(char)
        M_f = matrix(F, M_zz)
        C_f = matrix(F, C_zz)
        
        char_poly = M_f.charpoly()
        factors = char_poly.factor()
        
        for g_i, e_i in factors:
            deg = g_i.degree()
            if g_i == x or deg <= 1: # 跳過 deg 1 以避免 mod 1 的情況
                continue
            
            print(f"    [-] Found irreducible factor of degree {deg}")
            K = GF(char**deg, name='z', modulus=g_i)
            lmbda = K.gen()
            
            MK = M_f.change_ring(K)
            CK = C_f.change_ring(K)
            IK = identity_matrix(K, M_f.nrows())
            
            try:
                # 尋找特徵向量
                kernel = (MK - lmbda * IK).right_kernel()
                if kernel.dimension() == 0: continue
                w = kernel.basis()[0]
                
                # 計算 mu = Cw / w
                Cw = CK * w
                idx = 0
                while idx < len(w) and w[idx] == 0: idx += 1
                if idx == len(w): continue
                mu = Cw[idx] / w[idx]
                
                # --- 修正處：手動計算 order 並使用 discrete_log ---
                # 擴域群階為 char^deg - 1
                group_order = char**deg - 1
                
                # 使用 Sage 頂層 discrete_log 並指定 order 避開 PARI fflog 錯誤
                k_i = discrete_log(mu, lmbda, ord=group_order, operation='*')
                
                results.append(k_i)
                moduli.append(group_order)
                print(f"        [!] Local dlog SUCCESS: (mod {group_order})")
                
                # 累積足夠的模數就提早結束 (128 bits)
                current_lcm = lcm(moduli)
                if current_lcm.bit_length() > 140:
                    print(f"[+] Sufficient information collected ({current_lcm.bit_length()} bits)")
                    return True
            except Exception as e:
                print(f"        [?] Skip factor {deg}: {e}")
                continue
        return False

    # 依序榨乾 GF(2) 和 GF(3) 的資訊
    collect_dlog_info(2)
    collect_dlog_info(3)
    collect_dlog_info(5)
    collect_dlog_info(7)
    collect_dlog_info(11)
    collect_dlog_info(13)

    # --- CRT 合併 ---
    print("[*] Combining results with CRT...")
    try:
        # 使用逐步合併法處理不互質的 moduli
        cur_res = results[0]
        cur_mod = moduli[0]
        for i in range(1, len(results)):
            try:
                cur_res = crt([cur_res, results[i]], [cur_mod, moduli[i]])
                cur_mod = lcm(cur_mod, moduli[i])
            except ValueError:
                continue # 忽略不相容的解
        
        # 最終檢查與解密
        print(f"[+] Final k candidate found: {cur_res}")
        # 因為 key 可能超過 128 bit 或需要取模，我們取前 16 bytes
        # 正常的 k 應該就等於 key
        key_bytes = long_to_bytes(int(cur_res), 16)
        print(f"[*] AES Key: {key_bytes.hex()}")
        
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        flag = unpad(cipher.decrypt(enc_flag), 16)
        print("\n" + "!" * 50)
        print(f"FLAG: {flag.decode()}")
        print("!" * 50)
        
    except Exception as e:
        print(f"[-] Final Step Error: {e}")

if __name__ == "__main__":
    solve()
