import random
from flags import flag

base = 86844066927987146567678238756515930889952488499230423029593188005934867676767
seed = random.getrandbits(6767)
random.seed(seed)

for i in range(10):
    print("<", random.getrandbits(256))


a = int(input("a>"))
b = int(input("b>"))

if a==0 or a==1:
    print("[-] bad hacker")
    exit()

random.seed(a*seed + b)

for i in range(10):
    cur = int(input("> "))
    if random.randrange(base) != cur:
        print("[-] byebye")
        exit()

print("[+]", flag)
