import random

base_prime = 1143710000253594786648593806001124988802924174575621101137352008140273794347

def check_prime(n):
    for _ in range(120):
        if pow(random.randrange(1, n), n - 1, n) != 1:
            return False
    return True

# bad bad coding style :> (^ owO ^)

def gen_primes():
    new_primes = []
    tiny_step = 1<<16
    
    while len(new_primes) != 2:

        if len(new_primes) == 0:
            step = 1
            for i in range(7):
                step *= random.getrandbits(33)

        p1, p2 = step*base_prime + 1, (tiny_step + step)*base_prime + 1
        
        if check_prime(p1) and len(new_primes) == 0:
            new_primes.append(p1)
        
        if check_prime(p2):
            new_primes.append(p2)

        tiny_step += 2
    
    return new_primes

banner = """===========================================
🐿🪑🎹> Welcome 2 Squirrel Call System .....

 ,;;:;,
   ;;;;;
  ,:;;:;    ,'=.
  ;:;:;' .=" ,'_\\
  ':;:;,/  ,__:=@
   ';;:;  =./)_
     `"=\\_  )_"`
          ``'"`

Contributed by: 🐋.120 with heart :)
I don't like Oracles, but I love 🐿 calls
==========================================="""