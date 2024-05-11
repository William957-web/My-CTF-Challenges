from Crypto.Util.number import *
msg=[b'ICED{Br0DcasT_Att@ck_is_c00l_what_ab0u7_Boneh&Durfee?}']*3+[b'347ing_E47ing_EA7ing_EATing', b'I\'m still haunted by the memories', b'I\'m hurting baby, I\'m broken down', b'The Universe is going to put you in the right place, at the right time.', b'TMI=Too Much Informations', b'This challenge is not small e attack', b'Try to find out the three same messages', b'wwwWwWwWWWWWWWWWWwwwW']
msg=msg[2:5]+[msg[0]]+msg[5:7]+[msg[1]]+msg[7:11]
e=3
for i in range(11):
    print(f'*****   Message{i+1}:   *****')
    p, q=getPrime(512), getPrime(512)
    n=p*q
    c=pow(bytes_to_long(msg[0]), e, n)
    print(f"{c=}\n{e=}\n{n=}\n")
