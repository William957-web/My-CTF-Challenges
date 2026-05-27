import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from shared.zkp import N, compute_proof, decode_suffix, load_flag

FLAG = load_flag()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/prove":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"no")
            return
        query = parse_qs(parsed.query, keep_blank_values=True)
        if "d" not in query or "p" not in query or "s" not in query:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"missing")
            return
        try:
            user_part = decode_suffix(query["d"][0])
            server_part = decode_suffix(query["p"][0])
            suffix = user_part + server_part
            seed = int(query["s"][0])
            bit_flip_indices = [int(index) for index in query.get("f", [])]
            if not 2 <= seed < N:
                raise ValueError
            proof = compute_proof(FLAG, suffix, seed, bit_flip_indices=bit_flip_indices)
        except Exception:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"invalid")
            return
        body = json.dumps({"proof": proof}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        return


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
