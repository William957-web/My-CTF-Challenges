import json
import sys
import urllib.parse
import urllib.request


base = sys.argv[1].rstrip("/")
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
pow_info = json.loads(opener.open(base + "/pow").read().decode())

n = int(pow_info["n"])
e = int(pow_info["e"])
bits = int(pow_info["bits"])
challenge = int(pow_info["challenge"])
mask = (1 << bits) - 1

m = 0
while True:
    if pow(m, e, n) & mask == challenge:
        print(m)
        break
    m += 1

if len(sys.argv) > 2:
    data = urllib.parse.urlencode({"url": sys.argv[2], "m": str(m)}).encode()
    print(opener.open(base + "/bot", data=data).read().decode())
