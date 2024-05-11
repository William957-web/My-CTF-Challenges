from itertools import permutations
from hashlib import md5
wordlist=[b'Julian', b'Paul', b'Shiro', b'AU', b'Australia', b'TW', b'Taiwan', b'teddybear', b'2000', b'0607', b'nogamenolife', b'whale', b'shark']
def gen(x):
    s=b''
    for i in x:
        s+=i
    return s

for i in range(1, 5):
    for j in permutations(wordlist,i):
        if md5(gen(j)).hexdigest()=='f79975048e623bce754379568af584a3':
            print(gen(j))
            break
