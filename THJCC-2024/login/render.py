from flask import *
import os
from hashlib import *
app = Flask(__name__)

secret=open('secret', 'rb').read()
@app.route("/hello")
def hello():
    return "Hello, World!"

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        file=open('userlist.txt', 'rb')
        list_f=file.read()
        if f"{username}:" not in str(list_f):
            return "<h1>Error</h1><br></br><h2>帳號不存在</h2>"
        elif f"{username}:{password}" not in str(list_f):
            return "<h1>Error</h1><br></br><h2>密碼錯誤</h2>"
        else:
            response = make_response(redirect('/'))
            response.set_cookie('username', username)
        return response


@app.route("/home")
@app.route("/")
def index():
    if request.cookies.get('username')=='test':
        response = 'Hello World, You are only user right now'
    elif request.cookies.get('username')=='admin':
        response = make_response(redirect('/@meow'))
    else:
        response = make_response(redirect('/login'))
    return response

@app.route('/@<username>')
def say(username):
    if request.cookies.get('username')=='admin':
        return render_template_string('<!---What is render SSTI?--->\n<!---RCE me plz--->\nCat say ' + username)
    else :
        return 'you are not admin'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=33333) 
