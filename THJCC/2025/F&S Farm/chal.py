from Crypto.Util.number import bytes_to_long
from secrets import flag

p=62879100257270410351378827582399744186567306643585504679294001019813699019068488434060287
G=(29744250428373565997166706391119259777317687430240284769755486706450263827970573185114321, 58040952245003801555956486798081163256240960098545028765546427006596708448541303071682039, 27494033982261584279714070225528681888589641976608352586941470965443043075381645410758543)
a=0x1ced7ea
k=Integer(bytes_to_long(flag))

def point_add_mod(P, Q, a, p):
    X1, Y1, Z1 = P
    X2, Y2, Z2 = Q
    
    if Z1 % p == 0:
        return Q
    if Z2 % p == 0:
        return P
    
    Z1_sq = pow(Z1, 2, p)
    Z2_sq = pow(Z2, 2, p)
    U1 = (X1 * Z2_sq) % p
    U2 = (X2 * Z1_sq) % p
    S1 = (Y1 * pow(Z2, 3, p)) % p
    S2 = (Y2 * pow(Z1, 3, p)) % p
    
    H = (U2 - U1) % p
    R = (S2 - S1) % p
   
    if H % p == 0:
        if R % p == 0:
            return point_double_mod(P, a, p)
        else:
            return (0, 1, 0)
    
    H_sq = pow(H, 2, p)
    H_cu = pow(H, 3, p)
    R_sq = pow(R, 2, p)
    
    X3 = (R_sq - H_cu - 2 * U1 * H_sq) % p
    Y3 = (R * (U1 * H_sq - X3) - S1 * H_cu) % p
    Z3 = (Z1 * Z2 * H) % p
    
    return (X3, Y3, Z3)

def point_double_mod(P, a, p):
    X1, Y1, Z1 = P
    
    if Z1 % p == 0:
        return (0, 1, 0)
    
    Y1_sq = pow(Y1, 2, p)
    A = pow(X1, 2, p)
    B = Y1_sq
    C = pow(B, 2, p)
    D = (2 * ((pow(X1 + B, 2, p) - A - C))) % p 
    E = (3 * A + a * pow(Z1, 4, p)) % p
    F = pow(E, 2, p)
    
    X3 = (F - 2 * D) % p
    Y3 = (E * (D - X3) - 8 * C) % p
    Z3 = (2 * Y1 * Z1) % p
    
    return (X3, Y3, Z3)

def point_scalar_mult(k, P, a, p):
    result = (0, 1, 0)
    if k == 0 or P == (0, 1, 0):
        return result
    
    Q = P
    for bit in reversed(k.bits()):
        result = point_double_mod(result, a, p)
        if bit == 1:
            result = point_add_mod(result, Q, a, p)
    
    return result

print(point_scalar_mult(k, G, a, p))
# (11124982001864013322453099807532963752362958176203400769835646437519628542120137037648651, 6911772123608455530174938059753499932701792542764880851311370143692220479290267649006859, 61659910325477356427200894513232023552537183179022949708356534152728209603841725323867499)