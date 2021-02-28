from flask      import Flask, request, jsonify, current_app, g, flash, json
from flask_jwt_extended import *
from flask_cors import CORS
from sqlalchemy import create_engine, text
from datetime   import datetime, timedelta
from werkzeug.exceptions import HTTPException, NotFound
from utils import SECRET_KEY, ALGORITHM
from summarize import total, make_summary
from qna import ai_qna
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


def get_user_id(request):
    token = request.headers.get('Authorization')
    payload = jwt.decode(token, SECRET_KEY, ALGORITHM)

    return payload['user_id']


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
            password,
            name
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
    user_id = get_user_id(request)

    if request.method == 'POST':
        req = request.json
        bf_summary = req['text']
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
            :text,
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
        else:
            abort(question_arr)


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
    user_id = get_user_id(request)
    quizes = req['quiz_list']
    data = {}
    data['correct_list'] = []
    response = {}
    correct_num = 0
    for quiz in quizes:
        result = app.database.execute(text("""
        SELECTd
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

@app.route('/api/mypagequiz')
def mypagequiz():
    response = {}
    data = {}
    user_id = get_user_id(request)
    results = app.database.execute(text("""
        SELECT
            *
        FROM Quiz
        WHERE user_id = :user_id 
    """), {'user_id': user_id}).fetchall()

    quiz_list = []
    quizes = []
    last_index = results[0][5]
    last_quiz_id = results[-1][0]
    for result in results:
        quiz = {}
        quiz['quiz_id'] = result[0]
        quiz['quiz_type'] = result[1]
        quiz['quiz_content'] = result[2]
        #quiz['quiz_date'] = result[3]
        quiz['summary_id'] = result[5]
        quiz['book_title'] = result[6]
        quiz['my_answer'] = result[7]
        quiz['correct_answer'] = result[8]
        quiz['correct'] = result[9]
        if quiz['quiz_id'] == last_quiz_id:
            quizes.append(quiz)
            dt = {}
            dt['quiz'] = []
            for i in quizes:
                dt['quiz'].append(i)
            dt['summary_id'] = result[5]
            quiz_list.append(dt)
            quizes.clear()

        elif last_index != result[5]:
            dt = {}
            dt['quiz'] = []
            for i in quizes:
                dt['quiz'].append(i)
            dt['summary_id'] = last_index
            quiz_list.append(dt)
            quizes.clear()
            last_index = result[5]
        if quiz['quiz_id'] != last_quiz_id: quizes.append(quiz)

    data['quiz_list'] = quiz_list
    data['user_id'] = user_id
    
    response['status'] = '200'
    response['success'] = True
    response['message'] = "사용자의 퀴즈를 가져옵니다"
    response['data'] = data

    return jsonify(response)

@app.route('/api/userSummary')
def userSummary():
    response = {}
    data = {}
    user_id = get_user_id(request)
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

    data['summary_result'] = summary_r
    
    return jsonify({
        "status": 200,
        "success": True,
        "message": "사용자 요약 보여주기",
        "data": data
    })


@app.route('/api/allSummary')
def allSummary():
    response = {}
    data = {}
    summary_arr = []
    results = app.database.execute(text("""
        SELECT
            *
        FROM Summary
    """)).fetchall()
    for result in results:
        summary = {}
        summary['summary_id'] = result[0]
        summary['user_id'] = result[1]
        summary['summary_title'] = result[2]
        summary['content'] = result[4]
        summary['book_title'] = result[7]
        summary['book_author'] = result[8]
        summary_arr.append(summary)
    data['summary'] = summary_arr

    return jsonify({
        "status": 200,
        "success": True,
        "message": "모든 요약 반환",
        "data": data
    })    
    
@app.route('/api/qna', methods=['GET'])
def qna():
    user_id = get_user_id(request)
    summary = request.json
    summary_id = summary['summary_id']
    question = summary['question']

    bf_summary = app.database.execute(text("""
        SELECT
            bf_summary
        FROM Summary
        WHERE summary_id = :summary_id
    """), {'summary_id': summary_id}).fetchone()

    answer, confidence = ai_qna(bf_summary, question)
    data = {}
    data['answer'] = answer
    data['confidence'] = confidence

    if confidence >= 50:
        return jsonify({
            "status": 200,
            "success": True,
            "message": "질의응답 성공 (신뢰도 50 이상)",
            "data": data
        })
    else:
        return jsonify({
            "status": 200,
            "success": True,
            "message": "질의응답 성공 (신뢰도 50 이하)",
            "data": data
        })




if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
