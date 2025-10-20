import os
import json
import secrets
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import data_process
import signer
from hashlib import sha256

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

data_process.init_db()

DAEMONS = [
    ("systemd", "A system and service manager."),
    ("crond", "A daemon to execute scheduled commands."),
    ("sshd", "The OpenSSH daemon."),
    ("httpd", "The Apache HTTP server."),
    ("mysqld", "The MySQL database server."),
    ("nginx", "An HTTP and reverse proxy server."),
    ("dbus-daemon", "A message bus system."),
    ("cupsd", "The CUPS print server."),
    ("udevd", "A device manager for the Linux kernel."),
    ("smbd", "The Samba daemon for file and print services."),
    ("rsyslogd", "A logging daemon."),
    ("NetworkManager", "A daemon for managing network connections."),
    ("polkitd", "Authorization manager for applications."),
    ("named", "The BIND DNS daemon."),
    ("postfix", "A mail transfer agent."),
    ("iptables", "A user-space firewall utility."),
    ("auditd", "The Linux Audit System daemon."),
    ("wpa_supplicant", "A Wi-Fi Protected Access client."),
    ("dhcpd", "A DHCP server daemon."),
    ("nfsd", "The NFS server kernel thread daemon."),
    ("rpcbind", "A server that converts universal addresses to program numbers."),
    ("avahi-daemon", "A zero-configuration networking daemon."),
    ("snapd", "A daemon for managing snap packages."),
    ("containerd", "A container runtime daemon."),
    ("dockerd", "The Docker daemon."),
    ("lighttpd", "A lightweight web server."),
    ("vlc", "A multimedia player daemon."),
    ("chronyd", "A daemon for time synchronization."),
    ("pulseaudio", "A sound system daemon."),
    ("modemmanager", "A service for managing modems."),
    ("upowerd", "A service for power management."),
    ("squirreld", "🐿️🪑🎹.")
]

# whale.120

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('game'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        user_id = data_process.check_password(username, password)
        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('game'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if data_process.register(username, password):
            return redirect(url_for('login'))
        else:
            return render_template('register.html', error="Registration failed. Username may already exist or contain invalid characters.")
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/game')
def game():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    username = session['username']
    keys = data_process.get_keys(user_id)
    return render_template('game.html', username=username, pub_mask=keys['pub_mask'], pub_vector=keys['pub_vector'], generator_proof=sha256(str(keys['generator']).encode()).hexdigest())

@app.route('/get_balance')
def get_balance():
    if 'username' in session:
        conn = data_process.sqlite3.connect(data_process.DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT balance FROM users WHERE name=?", (session['username'].lower(),))
        balance = cur.fetchone()[0]
        conn.close()
        return jsonify({"balance": balance})
    return jsonify({"error": "Not logged in"}), 401

@app.route('/draw', methods=['POST'])
def draw():
    if 'user_id' not in session:
        return jsonify({"error": "Not logged in"}), 401

    if not data_process.buy_card(session['user_id']):
        return jsonify({"error": "Insufficient balance or account LOCKED (as much 9 trials are available)"}), 400

    try:
        data = request.json
        if not data or 'numbers' not in data or len(data['numbers']) != 9:
            data_process.coupon(session['username']) # Refund
            return jsonify({"error": "Invalid input data"}), 400

        user_input_vector = [int(n, 16) for n in data['numbers']]
        
        keys = data_process.get_keys(session['user_id'])
        if not keys:
            data_process.coupon(session['username']) # Refund
            return jsonify({"error": "User keys not found"}), 400

        verification1 = signer.vector_dot_vector(signer.array_row_dot_vector(keys['generator'], user_input_vector), keys['pub_mask'])
        verification2 = signer.vector_dot_vector(keys['pub_vector'], user_input_vector)

        if verification1 != verification2:
            data_process.coupon(session['username']) # Refund
            return jsonify({"error": "Verification failed"}), 400

        card_id_vector = signer.array_row_dot_vector(keys['generator'], user_input_vector)
        print(card_id_vector)
        daemon_name = DAEMONS[card_id_vector[0]%32][0]
        daemon_desc = DAEMONS[card_id_vector[1]%32][1]
        card_id = card_id_vector[2]
        
        # Check Flag
        flag_found = False
        if len(card_id_vector) == 3:
            print('meow')
            if keys['generator'][0] == user_input_vector:
                flag_found = True
        
        response_data = {
            "name": daemon_name,
            "description": daemon_desc,
            "id": card_id,
            "flag": "FLAG{FAKE_FLAG}" if flag_found else None,
            "card_id_vector_for_proof": card_id_vector,
            "user_secret_key_hash": sha256(str(keys['generator']).encode()).hexdigest()
        }
        
        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1202)
