import json
import random
import os
import binascii

# we want to reveal the secret if 10 out of 11 geese leaders here
# When geese hold meetings, it’s a flap session.
p = 471783227105919165842741944821066246927786641093751959384273692130209415901228406897761212988660458934742298734399025424716250391843724961708678150841319006994563839411401495612538412975109499976207558612306657107937014605734460191009962680403849138371603477538074561531445054835120550424442421835395970173257601798132091403055689505612299398851179305703293
FLAG = 'QnQSec{test_flag_by_whale120}'

geese_count = 11
public_keys = [random.getrandbits(128) for _ in range(geese_count)]
private_keys = [binascii.crc32(os.urandom(3)) for _ in range(geese_count - 1)]
possible_ans = []

out_data = {"msg":"Welcome to the Republic of Geese Leading Session, not a flap session, but is really about the flag :>",
"public_keys": public_keys}
print(json.dumps(out_data))
in_data = json.loads(input())
private_keys.append(binascii.crc32(bytes.fromhex(in_data['key'])))
for i in range(geese_count):
    prod = 1
    for j in range(geese_count):
        if i!=j:
            prod *= pow(public_keys[j], private_keys[j], p)
            prod %= p
    possible_ans.append(prod)

private_keys = []

out_data = {"msg":"you can prove if they cheat on u, key without u ...",
"checker":possible_ans[-1]}
print(json.dumps(out_data))
in_data = json.loads(input())
if in_data['cmd'] != 'reveal_flag':
    out_data = {"msg":"Bye bye~"}
    print(json.dumps(out_data))
    exit()

out_data = {"msg":"Let me check your goosy keys"}
print(json.dumps(out_data))
in_data = json.loads(input())
for i in range(geese_count):
    private_keys.append(binascii.crc32(bytes.fromhex(in_data['keys'][i])))

for i in range(geese_count):
    prod = 1
    for j in range(geese_count):
        if i!=j:
            prod *= pow(public_keys[j], private_keys[j], p)
            prod %= p

    if prod in possible_ans:
        out_data = {"msg":FLAG}
        print(json.dumps(out_data))
        exit()

out_data = {"msg":"KEYS FAILED qWq"}
print(json.dumps(out_data))
exit()
