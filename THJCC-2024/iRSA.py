from Crypto.Util.number import *
from collections import namedtuple


# define complex number
Complex=namedtuple("Complex", "r c")

# define complex multiplication
def Complex_Mul(P, Q):
    R=P.r*Q.r-P.c*Q.c
    C=P.r*Q.c+Q.r*P.c
    return Complex(R, C)

# define how to turn message into complex number
def Int_to_Complex(x):
    R=0
    C=0
    cnt=0
    while(x>0):
        if(cnt%2==0):
            R+=(x%2)<<cnt
        else:
            C+=(x%2)<<cnt
        x>>=1
        cnt+=1
    return Complex(R, C)

# keys
p, q=115354037749818467787883117855058744112232663945914692321109944593585909198619, 101215468079183132064927386006997214816266070286653603581590482424957134728767
P=Complex(p, 2*q)
Q=Complex(q, 2*p)
N=Complex_Mul(P, Q)

# generate flag
flag=b'THJCC{simple_high_school_math?!}'
m=bytes_to_long(flag)
M=Int_to_Complex(m)
e=65537
C=Complex(pow(M.r, e, N.r*-1), pow(M.c, e, N.c)) # N.r*-1 is because I don't want to define modular under negative number

print(f'{N=}')
print(f'{e=}, {C=}')