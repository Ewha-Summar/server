from flask      import Flask, request, jsonify, current_app, g, flash, json
from sqlalchemy import create_engine, text
from datetime   import datetime, timedelta
import bcrypt
import jwt
from werkzeug.exceptions import HTTPException, NotFound
from utils import SECRET_KEY, ALGORITHM
# import sys
# from os.path import dirname
# sys.path.append(dirname(__file__))

app = Flask(__name__)

#app.json_encoder = CustomJSONEncoder
app.config.from_pyfile("config.py")

# if test_config is None:
#     app.config.from_pyfile("config.py")
# else:
#     app.config.update(test_config)

database = create_engine(app.config['DB_URL'], encoding = 'utf-8', max_overflow = 0)
app.database = database

def get_user_id(user_id):
    sql = "SELECT user_id FROM user WHERE user_id = ?"
    rv = app.database.execute(sql, [user_id]).fetchone()  # 하나만 가져옴
    return rv[0] if rv else None

@app.errorhandler(HTTPException)
def error_handler(e):
    response = e.get_response()

    response.data = json.dumps({
        'status': e.code,
        'success': False,
        'message': e.description,
    })
    response.content_type = 'application/json'

    return response

@app.route("/signup", methods=['POST'])
def signup():
    new_user = request.json

    new_user['password'] = bcrypt.hashpw(new_user['password'].encode('utf-8'), bcrypt.gensalt()) # 비밀번호 해싱

    app.database.execute(text("""
        INSERT INTO user(
            user_id,
            password,
            name
        ) VALUES (
            :user_id,
            :password,
            :name
        )
    """), new_user)

    return jsonify({
        "status": 200,
        "success": True,
        "user_id": new_user['user_id'],
        "name": new_user['name']
    })

@app.route('/login', methods=['POST'])
def login():
    user = request.json
    user_id = user['user_id']
    password = user['password']

    row = app.database.execute(text("""
        SELECT
            user_id,
            password
        FROM user
        WHERE user_id = :user_id
    """), {'user_id' : user_id}).fetchone()
    

    # 입력한 비밀번호와 일치하는지 확인
    if row and bcrypt.checkpw(password.encode('utf-8'), row['password'].encode('utf-8')):
        user_id = row['user_id']
        payload = {
            'user_id' : user_id
        }
        token = jwt.encode(payload, SECRET_KEY, ALGORITHM)
        # print(token)

        return jsonify({
            'access_token': token
        })
    # 일치하지 않으면 : Unathorized status code
    else:
        return jsonify({
            "status": 401,
            "success": False,
            "message": "Incorrect password"
        })


app.run()