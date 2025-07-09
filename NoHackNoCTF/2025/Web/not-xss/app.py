from flask import Flask, request, render_template, jsonify, make_response, abort, session
from flask_cors import CORS
import subprocess
import threading
import hashlib
import os
import time

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.urandom(16)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5000"}}, supports_credentials=True)

FLAG = 'NHNC{B1g_c00k13_a193eb}'

def terminate_process(process):
    process.terminate()
    print("Process terminated after 20 seconds.")

def common_prefix(a: str, b: str) -> str:
    i = 0
    while i < len(a) and i < len(b) and a[i] == b[i]:
        i += 1
    return a[:i]

def restrict_remote_addr():
    if request.remote_addr != '127.0.0.1':
        abort(403)

@app.route('/get_challenge', methods=['GET'])
def get_challenge():
    challenge = os.urandom(8).hex()
    session['challenge'] = challenge
    session['ts'] = time.time()
    return jsonify({
        "challenge": challenge,
        "description": "Find a nonce such that SHA256(challenge + nonce) starts with 000000"
    })

@app.route('/visit', methods=['GET'])
def visit():
    url = request.args.get('url')
    nonce = request.args.get('nonce')

    if not url or not nonce:
        return "Missing url or nonce", 400

    if not url.startswith('http://'):
        return "Bad Hacker", 400

    challenge = session.get('challenge')
    ts = session.get('ts')

    if not challenge or not ts:
        return "No challenge in session. Please request /get_challenge first.", 400

    if time.time() - ts > 60:
        session.pop('challenge', None)
        session.pop('ts', None)
        return "Challenge expired. Please request a new one.", 400

    h = hashlib.sha256((challenge + nonce).encode()).hexdigest()
    if not h.startswith("000000"):
        return "Invalid PoW", 400

    # No reuse of PoW
    session.pop('challenge', None)
    session.pop('ts', None)

    process = subprocess.Popen(['chromium', url, '--headless', '--disable-gpu', '--no-sandbox', '--disable-popup-blocking'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    timer = threading.Timer(20, terminate_process, [process])
    timer.start()
    return "Admin is visiting your page!"

@app.route('/')
def index():
    restrict_remote_addr()
    return render_template('index.html')

@app.route('/inner.html')
def inner():
    restrict_remote_addr()
    return render_template('inner.html')


@app.route('/guess', methods=['POST'])
def guess():
    restrict_remote_addr()

    guess_str = request.form.get('guess')
    note = request.form.get('note')

    if not guess_str or not note:
        return jsonify({'error': 'invalid payload'}), 400
    current_shared = common_prefix(guess_str, FLAG)

    old = request.cookies.get('best', '')
    old_prefix = bytes.fromhex(old.split(':', 1)[0]).decode() if ':' in old else ''

    best_prefix = old_prefix if len(old_prefix) > len(current_shared) else current_shared

    resp = make_response(jsonify({'best_prefix': best_prefix, 'note': note}))
    resp.set_cookie('best', f"{best_prefix.encode().hex()}:{note.encode().hex()}")
    return resp 


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
