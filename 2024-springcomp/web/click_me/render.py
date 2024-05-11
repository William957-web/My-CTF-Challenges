from flask import *
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        res = request.form['flag']
        if res=='no':
            return render_template('display.html', msg='NO FLAG FOR YOU QQ')
        else:
            return render_template('display.html', msg='ICED{ofc_this_is_your_flag}')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)