from pwn import *
r=remote('23.146.248.36', 30003)
#r=remote('0.0.0.0', 29999)
s=r.recvlines(3)
print(s)
def judge(a):
    cnt=0
    ans=0
    for i in range(len(a)):
        cnt+=a[i]
        if i+1<len(a) and cnt<a[i+1]:
            ans=max(cnt, ans)
            cnt=0
    ans=max(ans, cnt)
    return ans

for i in range(3):
    s=r.recvline()
    print(s)
    for j in range(10):
        s=r.recvline()
        print(s)
        exec('a='+str(s)[2:-3])
#        print(a)
        r.sendline(str(judge(a)).encode())
        s=r.recvline()
        print(s)

r.interactive()
