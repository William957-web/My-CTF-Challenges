from random import getrandbits
from flags import flag

N = 528302026814581112698976132408136607344677298272713726039361987095410824358231139478581273

def oracle(trial, salt):
    assert 2 <= salt <= N-2
    cnt = 0
    for c in bin(trial)[2:]:
        if c == '0':
            cnt += salt
        else:
            cnt = pow(cnt, salt, N)
    return cnt

ans = getrandbits(256)
token = ans
TRIAL1 = 128
TRIAL2 = 128

print("option 1: guess\noption 2: adjust\nothers: buy me a pizza")

while TRIAL1 + TRIAL2 > 0:
    opt = input("option? ")
    if opt == '1':
        if TRIAL1 == 0:
            print("exhausted ...")
            continue
        TRIAL1 -= 1
        salt = int(input("salt? "))
        print(oracle(token, salt))
    elif opt == '2':
        if TRIAL2 == 0:
            print("exhausted ...")
            continue
        TRIAL2 -= 1
        salt = int(input("salt? "))
        assert salt.bit_count() == 1
        token = token ^ salt
    else:
        print("u better buy me a pizza!")
        exit()

guess = int(input("guess? "))

if guess == ans:
    print(flag)

else:
    print("awa")
