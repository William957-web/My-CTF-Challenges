import time
from random import *

time_limit = 5
def judge(a, x):
    cnt=0
    ans=0
    for i in range(len(a)):
        cnt+=a[i]
        if i+1<len(a) and cnt<a[i+1]:
            ans=max(cnt, ans)
            cnt=0
    ans=max(ans, cnt)
    if ans==x:
        return "AC"
    else:
        return "WA"

print("There are 30 test cases, once you AC all of them, you will get flag.")
print("Also, there are 10 cases for each round, so there are 3 rounds")
print("Plz notice that there's a time limit of 5 seconds")
score=0
# stage 1
print("=============== ROUND 1 ===============")
for i in range(10):
    a=[]
    for j in range(10):
        bits=randint(1, 10)
        a.append(randint(1, 2**bits))
    print(a)
    start = time.time()
    x=int(input())
    end = time.time()
    if judge(a, x)=="AC" and end-start<=5:
        score+=1
        print("AC")
    else:
        print("WA")

# stage 2
print("=============== ROUND 2 ===============")
for i in range(10):
    a=[]
    for j in range(1000):
        bits=randint(10, 20)
        a.append(randint(1, 2**bits))
    print(a)
    x=int(input())
    if judge(a, x)=="AC":
        score+=1
        print("AC")
    else:
        print("WA")

# stage 3
print("=============== ROUND 3 ===============")
for i in range(10):
    a=[]
    for j in range(100000): 
        bits=randint(20, 30)
        a.append(randint(1, 2**bits))
    print(a)
    x=int(input())
    if judge(a, x)=="AC":
        score+=1
        print("AC")
    else:
        print("WA")

if score==30:
    print("Delicious flag:THJCC{little_cat_meow_meow_meow}")
else:
    print(f"Your score is {score}, no flag for you qq")
    