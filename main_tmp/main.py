from flask      import Flask, request, jsonify, current_app, g, flash, json
from sqlalchemy import create_engine, text
from datetime   import datetime, timedelta
from werkzeug.exceptions import HTTPException, NotFound
from utils import SECRET_KEY, ALGORITHM
from summarize import total, make_summary
import bcrypt
import jwt

app = Flask(__name__)
app.config.from_pyfile("config.py")

database = create_engine(app.config['DB_URL'], encoding = 'utf-8', max_overflow = 0)
app.database = database

cors = CORS(app, resources = {
    r"/v1/*": {"origin": "*"},
    r"/api/*": {"origin": "*"}
    })

def get_user_id(user_id):
    sql = "SELECT user_id FROM User WHERE user_id = ?"
    rv = app.database.execute(sql, [user_id]).fetchone()
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

@app.route("/api/signup", methods=['POST'])
def signup():
    new_user = request.json

    new_user['password'] = bcrypt.hashpw(new_user['password'].encode('utf-8'), bcrypt.gensalt()) # 비밀번호 해싱

    app.database.execute(text("""
        INSERT INTO User(
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

@app.route('/api/login', methods=['POST'])
def login():
    user = request.json
    user_id = user['user_id']
    password = user['password']

    row = app.database.execute(text("""
        SELECT
            user_id,
            password
        FROM User
        WHERE user_id = :user_id
    """), {'user_id' : user_id}).fetchone()
    
    if row and bcrypt.checkpw(password.encode('utf-8'), row['password'].encode('utf-8')):
        user_id = row['user_id']
        name = row['name']
        payload = {
            'user_id' : user_id
        }
        token = jwt.encode(payload, SECRET_KEY, ALGORITHM)
        # print(token)

        return jsonify({
            "status": 200,
            "success": True,
            "message": "로그인 성공",
            "access_token": token,
            "user_id": user_id,
            "name": name
        })
    else:
        return jsonify({
            "status": 401,
            "success": False,
            "message": "Incorrect password"
        })

@app.route("/api/summary", methods=['POST'])
def summary():
    data = {}
    response = {}
    user_id = "test@naver.com"

    if request.method == 'POST':
        print(user_id)
        req = request.json
        bf_summary = req['bf_summary']
        count = req['count']
        input_type = req['input_type']
        summary_user, question_arr, result_arr = total(
            bf_summary, count, input_type)
        req['af_summary'] = summary_user
        req['user_id'] = user_id
        
        if result_arr is not None:
            app.database.execute(text("""
        INSERT INTO Summary(
            user_id,
            summary_title,
            bf_summary,
            af_summary,
            count,
            input_type,
            book_title,
            book_author
        ) VALUES (
            :user_id,
            :summary_title,
            :bf_summary,
            :af_summary,
            :count,
            :input_type,
            :book_title,
            :book_author
        )"""), req)

            
            sql = "SELECT LAST_INSERT_ID()"
            summary_id = app.database.execute(sql).fetchone()

            quiz_date = "2021-02-17"
            for i in range(len(question_arr)):
                req['quiz_type'] = 0
                req['quiz_content'] = question_arr[i]
                req['quiz_date'] = quiz_date
                req['user_id'] = user_id
                req['summary_id'] = summary_id[0]
                req['correct_answer'] = result_arr[i]
                app.database.execute(text("""
            INSERT INTO Quiz(
                quiz_type,
                quiz_content,
                quiz_date,
                user_id,
                summary_id,
                book_title,
                correct_answer
            ) VALUES (
                :quiz_type,
                :quiz_content,
                :quiz_date,
                :user_id,
                :summary_id,
                :book_title,
                :correct_answer
            )"""), req)

            response['status'] = 200
            response['success'] = True
            response['message'] = "요약 및 퀴즈를 생성합니다"
            data['content'] = summary_user
            data['summary_id'] = summary_id[0]
            response['data'] = data
            return jsonify(response)
        #error 발생 상황
        else:
            abort(question_arr)
        #result_arr가 None인 경우 question_arr에 responseCode가 저장되어 있음


@app.route('/api/summary', methods=['GET'])
def summary_return():
    summaryid = request.args.get('summary_id')
    data = {}
    data['content'] = app.database.execute(text("""
        SELECT
            af_summary
        FROM Summary
        WHERE summary_id = :summaryid
    """), {'summaryid': summaryid}).fetchone()[0]

    data['summary_id'] = summaryid

    response = {}
    response['status'] = 200
    response['success'] = True
    response['message'] = "요약을 반환합니다"
    response['data'] = data

    return jsonify(response)


@app.route('/api/quiz', methods=['GET'])
def quiz_return():
    quiz_type = request.args.get('quiz_type')
    summary_id = request.args.get('summary_id')
    data = {}
    response = {}
    data['quiz_list'] = []
    results = app.database.execute(text("""
        SELECT
            quiz_id,
            quiz_content
        FROM Quiz
        WHERE quiz_type = :quiz_type 
        and summary_id = :summary_id
    """), {'quiz_type': quiz_type, 'summary_id': summary_id}).fetchall()
    
    for result in results:
        quiz = {}
        quiz['quiz_id'] = result[0]
        quiz['content'] = result[1]
        data['quiz_list'].append(quiz)

    response['status'] = 200
    response['success'] = True
    response['message'] = "퀴즈를 가져옵니다"
    response['data'] = data

    return jsonify(response)


@app.route('/api/scoring', methods=['POST'])
def scoring():
    req = request.json
    user_id = 'test@naver.com'
    quizes = req['quiz_list']
    data = {}
    data['correct_list'] = []
    response = {}
    correct_num = 0
    for quiz in quizes:
        result = app.database.execute(text("""
        SELECT
            quiz_content,
            correct_answer
        FROM Quiz
        WHERE quiz_id = :quiz_id 
        """), quiz).fetchone()

        q = {}
        q['quiz_id'] = quiz['quiz_id']
        q['content'] = result[0]
        if quiz['my_answer'] == result[1]:
            q['correct'] = True
            quiz['correct'] = True
            correct_num += 1
        else:
            q['correct'] = False
            quiz['correct'] = False

        app.database.execute(text("""
        UPDATE Quiz
        SET
            my_answer = :my_answer,
            correct = :correct
        WHERE quiz_id = :quiz_id
        """), quiz)        
        data['correct_list'].append(q)
    data['score'] = correct_num/len(quizes)
    #data['score'] = str(correct_num) + '/' + str(len(quizes))

    scoreInfo = {}
    scoreInfo['user_id'] = user_id
    scoreInfo['summary_id'] = req['summary_id']
    scoreInfo['score'] = data['score']

    app.database.execute(text("""
    INSERT INTO Score(
        user_id, 
        summary_id, 
        score
    ) VALUES (
        :user_id,
        :summary_id,
        :score
    )
    """), scoreInfo)

    response['status'] = 200
    response['success'] = True
    response['message'] = "퀴즈를 채점합니다"
    response['data'] = data

    return jsonify(response)

'''
@app.route('/api/mypagequiz')
def mypagequiz():
    response = {}
    data = {}
    user_id = 'test@naver.com'
    results = app.database.execute(text("""
        SELECT
            *
        FROM Quiz
        WHERE user_id = :user_id 
    """), {'user_id': user_id}).fetchall()

    quiz_list = []
    for result in results:
        quiz = {}
        quiz['quiz_id'] = result[0]
        quiz['quiz_type'] = result[1]
        quiz['quiz_content'] = result[2]
        quiz['quiz_date'] = result[3]
        #quiz['summary_id'] = result[5]
        quiz['book_title'] = result[6]
        quiz['my_answer'] = result[7]
        quiz['correct_answer'] = result[8]
        quiz['correct'] = result[9]
        quiz_list[result[5]].append(quiz)
    
'''


@app.route('/api/userSummary')
def userSummary():
    response = {}
    data = {}
    user_id = 'test@naver.com'
    summary_r = []
    results = app.database.execute(text("""
        SELECT
            *
        FROM Summary
        WHERE user_id = :user_id 
    """), {'user_id': user_id}).fetchall()
    data['user_id'] = user_id
    for result in results:
        summary = {}
        summary['summary_id'] = result[0]
        summary['summary_title'] = result[2]
        summary['content'] = result[4]
        summary['book_title'] = result[7]
        summary['book_author'] = result[8]
        summary_r.append(summary)
        #book_title, author가 없는 경우에 index 에러 안나는지 확인 못해봄.
    response['status'] = 200
    response['success'] = True
    response['message'] = "사용자 요약 보여주기"
    data['summary_result'] = summary_r
    response['data'] = data

    return jsonify(response)

app.run()