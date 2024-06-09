from flask import Flask, render_template, request, redirect, url_for, session, g
from hashlib import md5
import sqlite3

app = Flask(__name__)
app.secret_key = 'Whale_eating_3@ting'

DATABASE = 'blog.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = md5(request.form['password'].encode()).hexdigest()
        db = get_db()
        cur = db.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        user = cur.fetchone()
        if user:
            session['logged_in'] = True
            session['username'] = username
            if username=='twitter_pwd':
                return render_template('login.html', msg='ICED{U_Just_H@ck3d_mY_Twitter_pwd!!!}')
            else:
                return render_template('login.html', msg=f'Welcome, user:{username}')
        else:
            return render_template('login.html', error='Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/post')
def view_post():
    post_id=request.args.get('id')
    db = get_db()
    cur = db.execute(f'SELECT * FROM posts WHERE id={post_id}')
    post = cur.fetchone()
    return render_template('post.html', post=post)

@app.route('/')
def index():
    db = get_db()
    cur = db.execute('SELECT * FROM posts ORDER BY id DESC')
    posts = cur.fetchall()
    return render_template('index.html', posts=posts)

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=80)
