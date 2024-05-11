from flask import *
import jwt
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'whale123'

def generate_jwt_token(is_admin):
    payload = {
        'is_admin': is_admin,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1000)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['is_admin']
    except jwt.ExpiredSignatureError:
        return False  # Token已过期
    except jwt.InvalidTokenError:
        return False  # Token无效

@app.route('/', methods=['GET'])
def index():
    token = request.cookies.get('jwt_token')
    if token:
        is_admin = verify_jwt_token(token)
        if is_admin:
            return "<h1>Welcome Admin!!!</h1><h3>NEXT CHALLENGE URL : https://secret-c4lculati0n.onrender.com</h3>"
        else:
            return "<h1>Welcome User!!!</h1><h3>We use JWT COOKIE 🍪 to identify users</h3>"
    else:
        response = make_response(redirect('/'))
        response.set_cookie('jwt_token', generate_jwt_token(False))
        return response
        


if __name__ == '__main__':
    app.run('0.0.0.0', 80)
