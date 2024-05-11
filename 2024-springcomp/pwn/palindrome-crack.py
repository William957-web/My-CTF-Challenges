from pwn import *
r=remote('23.146.248.20', 40001)
s=r.recvlines(2)
print(s)

for i in range(100):
    r.recvline()
    s=r.recvline().split(b"'")[1]
    if s==s[::-1]:
        r.sendline(b'YES')
    else:
        r.sendline(b'NO')
    print(r.recvline())

r.interactive()
