from sage.all import *
from Crypto.Util.number import *
import requests as req
import time
import random

url_base = 'http://10.120.0.3:1202/' # change me >w<
exp_string = chr(8490)+'ing_whale'+str(time.time())[-6:]
exp_session = req.session()

def register(username, password):
    web = req.post(url_base + 'register', data={'username':username, 'password':password})
    if web.status_code==200:
        print(f"[*] Successfully registered for {username}")
    else:
        print(web.text, web.status_code)
        exit("[-] Register failed")

def login(username, password):
    global exp_session
    web = exp_session.post(url_base + 'login', data={'username':username.lower(), 'password':password})
    if web.status_code == 200:
        print(f"[*] Successfully logged in as {username}")
    else:
        exit("[-] Login failed")

def game(payload_arr):
    web = exp_session.post(url_base+'draw', json={"numbers":[hex(_) for _ in payload_arr]})
    if web.json()['flag'] != None:
        print(f"Flag found: {web.json()['flag']}")
    return web.json()["card_id_vector_for_proof"]

exp_array = []
proof_array = []
public_array = []

for i in range(8):
    # Probably don't need as many as much, but I still use ;P
    cur_arr = []
    for j in range(9):
        cur_arr.append(random.getrandbits(2048))
    exp_array.append(cur_arr)

def extract_public(idx):
    global public_array, exp_array
    A = [[0]*18 for _ in range(10)]
    for i in range(9):
        A[i][i] = -1
        for j in range(8):
            A[i][9+j] = int(exp_array[j][i])
    
    A[-1][9] = random.getrandbits(4096)
    for i in range(8):
        A[-1][9+i] = int(proof_array[i][idx])
    
    A = Matrix(A)
    trial_M = A.LLL()
    for vc in trial_M:
        valid = True
        for i in range(9):
            if isPrime(int(vc[i])) == False:
                valid = False
        if valid == True:
            print(f"Found: {list(vc)[:9]}")
            return list(vc)[:9]
    
    exit("[-] Exploit Failed, linear not found")

for i in range(9):
    register(exp_string, exp_string)

login(exp_string, exp_string)
for i in range(8):
    proof_array.append(game(exp_array[i]))

for i in range(3):
    cur_vc = extract_public(i)
    public_array.append(cur_vc)


game(list(public_array[0]))