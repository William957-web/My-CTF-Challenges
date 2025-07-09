from flask import Flask, request, jsonify, abort, redirect, session, render_template, make_response
import subprocess
import threading
import hashlib
import os
import time

app = Flask(__name__)
app.secret_key = os.urandom(16)

FLAG = 'NHNC{javascript:xssed!&xssed!=alert(/whale/)}' 

def terminate_process(process):
    process.terminate()
    print("Process terminated after 20 seconds.")

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

    if not url.startswith('http://localhost:5000/'):
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

    process = subprocess.Popen(['chromium', url, '--headless', '--disable-gpu', '--no-sandbox'],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    timer = threading.Timer(20, terminate_process, [process])
    timer.start()
    return "Admin is visiting your page!"

@app.route('/', methods=['GET'])
def main():
    if request.remote_addr == '127.0.0.1':
        resp = make_response(render_template('index.html'))
        resp.set_cookie('flag', FLAG)
        return resp
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
