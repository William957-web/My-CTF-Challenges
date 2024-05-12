from pwn import *
from tqdm import *
r=remote('23.146.248.36', 20003)

def oracle(mess):
    s=r.recvlines(2)
    s=r.recvuntil(b':')
    r.sendline(b'2')
    s=r.recvuntil(b':')
    r.sendline(mess.hex().encode())
    return b'Correct' in r.recvline()



s=r.recvlines(6)
print(s)
s=r.recvuntil(b':')
r.sendline(b'2')
s=r.recvuntil(b':')
r.sendline(b'656174696e675f7768616c652e2e2e01')
sign=r.recvline()[:-1]
s=r.recvlines(3)
s=r.recvuntil(b':')
r.sendline(b'1')
s=r.recvuntil(b':')
r.sendline(sign)
s=r.recvlines(3)
enc_flag=bytes.fromhex(r.recvline()[:-1].decode())
s=r.recvlines(2)
s=r.recvuntil(b':')
r.sendline(b'1')
s=r.recvuntil(b':')
r.sendline(b'0'*64)
leak=bytes.fromhex(r.recvuntil(b'\n')[:-1].decode())
IV=xor(leak[0:16], leak[16:32])

flag=IV+enc_flag
ans=b''
cur=b''
#r.interactive()
for i in trange(0, len(flag)-16, 16):
    iv, mess=flag[i:i+16], flag[i+16:i+32]
    for j in trange(16):
        now=15-j
        for k in range(256):
            if oracle(iv[:now]+bytes([k])+xor(cur, iv[now+1:], chr(16-now).encode()*(15-now))+mess):
                if now==15:
                    if k!=iv[15]:
                        cur=xor(k, iv[15], 1)+cur
                        break
                else:
                    cur=xor(k, iv[now], (16-now))+cur
                    break
    ans+=cur
    print(ans)
    cur=b''
