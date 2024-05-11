import base64
passkey=b'+-6>*0\x0c. J\x08I\x1bK*\x1e"<:\r5IAM\x1aK.\x01 J"\x08\x1b\x166H I:M)IA\x12\x19?>\x0b\x1a?.\r"J.A'
s=input("Enter your secret:")
def xor(x, y):
    z=''
    for i in y:
        z+=chr(i^x)
    return z.encode()

if xor(120, base64.b64encode(s.encode()))==passkey:
    print("Password Correct!!!")

else:
    print("Password Incorrect QQ")
