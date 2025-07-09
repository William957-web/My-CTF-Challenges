from random import getrandbits
import os
import hashlib

flag=os.urandom(8).hex()
keys=[getrandbits(48) for _ in range(16)]

def to_complex(datas):
    imag_datas=[]
    for i in range(0, len(datas), 2):
        imag_datas.append(CC([datas[i], datas[i+1]]))
    return imag_datas

imag_flag=to_complex([int(chr, 16) for chr in flag])
imag_keys=to_complex(keys)

cnt=0
for i in range(8):
    cnt+=imag_flag[i]*imag_keys[i]

print(f"{imag_keys}\n{cnt}")
print(f"Gift: {hashlib.md5(b'THJCC{'+flag.encode()+b'}').hexdigest()}")

# [9.83329568728950e13 + 1.94539067458416e14*I, 4.57795946512170e13 + 5.54913449090490e13*I, 3.35752608137010e13 + 1.10651091133529e14*I, 8.09172050820060e13 + 6.09012985967910e13*I, 2.75388068605530e13 + 5.12867910525740e13*I, 2.33510497525684e14 + 9.11264352204540e13*I, 2.36186170290599e14 + 2.03323868604921e14*I, 1.37793863865401e14 + 1.40354868241912e14*I]
# 3.22421607806873e14 + 1.37668712938916E+16*I
# Gift: 69ae60327282356b2f2731e6acf624f4