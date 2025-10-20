import sqlite3
import hashlib
import json
import signer

DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        password TEXT NOT NULL,
        keys TEXT NOT NULL,
        balance INTEGER NOT NULL DEFAULT 0,
        trials INTERGER NOT NULL DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

def sha256_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def check_exist(username: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE LOWER(name)=LOWER(?)", (username,))
    result = cur.fetchone()
    conn.close()
    return result is not None

def check_password(username: str, password: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, password FROM users WHERE LOWER(name)=LOWER(?)", (username,))
    row = cur.fetchone()
    conn.close()

    if row:
        user_id, stored_password = row
        if sha256_hash(password) == stored_password:
            return user_id
    return None

def coupon(username: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET balance = balance + 50 WHERE name=?", (username.lower(),))
    conn.commit()
    conn.close()

def buy_card(user_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH)
    conn.isolation_level = None
    cur = conn.cursor()

    try:
        cur.execute("BEGIN IMMEDIATE TRANSACTION")

        cur.execute("""
            UPDATE users
            SET balance = balance - 50, trials = trials + 1
            WHERE id = ? AND balance >= 50 AND trials < 9
        """, (user_id,))

        if cur.rowcount == 1:
            conn.commit()
            return True
        else:
            conn.rollback()
            return False
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()


def register(username: str, password: str):
    if check_exist(username) or len(username) > 32:
        return False
    
    allowed_chars = '0123456789abcdefghijklmnopqrstuvwxyz._-'
    for c in username.lower():
        if c not in allowed_chars:
            return False

    hashed_password = sha256_hash(password)
    keys_dict = signer.gen_keys()
    keys_json = json.dumps(keys_dict)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, password, keys, balance) VALUES (?, ?, ?, ?)",
                (username.lower(), hashed_password, keys_json, 0))
    conn.commit()
    conn.close()

    coupon(username)
    return True

def get_keys(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT keys FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None
