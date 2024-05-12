from Crypto.Util.number import *
from sympy import *
from random import *
p=22954440473064692367638020521915192869513867655951252438024058919141
plist=factorint(p-1)
while True:
    cur=randint(2**220, 2**221)
    tt=True
    for i in plist:
        if pow(cur, (p-1)//i, p)==1:
            tt=false
            break
    if tt:
        s=randint(2**200, 2**210)*1004
        print(f'({cur-s}, {s//1004})')