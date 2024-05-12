from flask import *
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        if username=="admin" and password=="iloveshark":
            return "THJCC{w31c0me_h@cker}"
        else:
            return '<h1>login failed</h1><a href="login">Click me</a>'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=13370) 