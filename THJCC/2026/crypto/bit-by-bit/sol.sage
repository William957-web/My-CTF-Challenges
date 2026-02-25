from Crypto.Util.number import *
import json

with open('output.txt', 'r') as f:
    datas = json.load(f)

cs = []
Ns = []

def get_flag(key):
    flag = 0
    global cs, Ns
    for i in range(len(cs)):
        if int(bytes_to_long(key)) % Ns[i] == int(cs[i]):
            flag += 1
        if i!=len(cs)-1:
            flag *= 2
    print(long_to_bytes(flag))

for cur_data in datas:
    cur_N = cur_data[1]
    cur_c = cur_data[0]
    cur_d = pow(0x10001, -1, euler_phi(cur_N))
    Ns.append(cur_N)
    cs.append(int(pow(cur_c, cur_d, cur_N)))

R=crt(cs, Ns)
N = 1

for i in Ns:
    N*=i

P.<x> = PolynomialRing(Zmod(N))
f = x-R

for i in range(30, 70):
    key = f.small_roots(beta=i/100)
    print(i)
    if len(key)>0:
        cur_key = long_to_bytes(int(key[0]))
        print(cur_key, len(cur_key))
        print(get_flag(cur_key))