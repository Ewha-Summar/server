from flask      import Flask, request, jsonify, current_app, g, flash, json
from flask_cors import CORS
from sqlalchemy import create_engine, text
from datetime   import datetime, timedelta
from werkzeug.exceptions import HTTPException, NotFound
from utils import SECRET_KEY, ALGORITHM
from summarize import total, make_summary
from qna import ai_qna
from OpenSSL import SSL
import datetime as dt
import bcrypt
import jwt
import ssl

app = Flask(__name__)
app.config.from_pyfile("config.py")

database = create_engine(app.config['DB_URL'], encoding = 'utf-8', max_overflow = 0)
app.database = database

cors = CORS(app, resources = {
    r"/v1/*": {"origin": "*"},
    r"/api/*": {"origin": "*"}
    })

#context = SSL.Context(SSL.SSLv3_METHOD)
#cert = 'private.pem'
#pkey = 'private.key'
#context.use_privatekey_file(pkey)
#context.use_certificate_file(cert)

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
    """), new_user)#유저 정보 db삽입

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

    result = app.database.execute(text("""
        SELECT
            user_id,
            password,
            name
        FROM User
        WHERE user_id = :user_id
    """), {'user_id' : user_id}).fetchone()#user_id에 해당하는 정보 불러오기
    
    if result is None:
        return jsonify({
            "status": 401,
            "success": False,
            "message": "아이디가 없습니다"
        })#일치하는 아이디가 없음

    if result and bcrypt.checkpw(password.encode('utf-8'), result['password'].encode('utf-8')):
        user_id = result['user_id']
        name = result['name']
        payload = {
            'user_id' : user_id
        }
        token = jwt.encode(payload, SECRET_KEY, ALGORITHM)#토큰생성

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
    if user_id is None:
        return jsonify({
            "status": 401,
            "success": False,
            "message": "로그인이 필요합니다"
        })

    if request.method == 'POST':
        req = request.json

        count = req['count']
        bf_summary = req['text']
        input_type = req['input_type']
        keyword = req['keyword']
        summary_user, question_arr, result_arr = total(bf_summary, count, input_type, keyword)

        req['af_summary'] = summary_user
        req['user_id'] = user_id

        #result_arr : 퀴즈에 대한 정답 배열
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
        )"""), req)#summary 정보 db 삽입

            sql = "SELECT Max(summary_id) FROM summardb.Summary"
            summary_id = app.database.execute(sql).fetchone()#삽입한 summary의 summary_id
            summary_id = int(summary_id[0])
            quiz_date = dt.datetime.now()

            for i in range(len(question_arr)):
                req['quiz_type'] = 0
                req['quiz_content'] = question_arr[i]
                req['quiz_date'] = quiz_date
                req['user_id'] = user_id
                req['summary_id'] = summary_id
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
            )"""), req)#퀴즈 정보 db 삽입

            data['content'] = summary_user
            data['summary_id'] = summary_id

            return jsonify({
                "status": 200,
                "success": True,
                "message": "요약 및 퀴즈를 생성합니다",
                "data": data
            })
        else:
            abort(question_arr)#result_arr 가 None인 경우, question_arr에 response code가 저장되어 있음


@app.route('/api/summary', methods=['GET'])
def summary_return():
    summaryid = request.args.get('summary_id')
    data = {}
    data['summary_id'] = summaryid
    data['content'] = app.database.execute(text("""
        SELECT
            af_summary
        FROM Summary
        WHERE summary_id = :summaryid
    """), {'summaryid': summaryid}).fetchone()[0]#저장된 summary

    if data['content'] is None:
        return jsonify({
            "status": 400,
            "success": False,
            "message": "존재하지 않는 요약입니다"
        })

    return jsonify({
        "status": 200,
        "success": True,
        "message": "요약을 반환합니다",
        "data": data
    })


@app.route('/api/quiz', methods=['GET'])
def quiz_return():
    quiz_type = request.args.get('quiz_type')
    summary_id = request.args.get('summary_id')

    data = {}
    data['quiz_list'] = []

    id = app.database.execute(text("""
        SELECT
            user_id
        FROM Quiz
        WHERE summary_id = :summary_id
    """), {'summary_id': summary_id}).fetchall()#요청된 summary의 user_id

    user_id = get_user_id(request)#요청자의 user_id

    '''
    if user_id != id:
        return jsonify({
            "status": 401,
            "success": False,
            "message": "권한이 없습니다"
        })#두 아이디가 일치하지 않을 경우 권한 없음
    '''

    results = app.database.execute(text("""
        SELECT
            quiz_id,
            quiz_content
        FROM Quiz
        WHERE quiz_type = :quiz_type 
        and summary_id = :summary_id
    """), {'quiz_type': quiz_type, 'summary_id': summary_id}).fetchall()#요청 summary에 해당하는 quiz list
    
    for result in results:
        quiz = {}
        quiz['quiz_id'] = result[0]
        quiz['content'] = result[1]
        data['quiz_list'].append(quiz)
        #quiz list를 json 배열로 변환


    return jsonify({
        "status": 200,
        "success": True,
        "message": "퀴즈를 가져옵니다",
        "data": data
    })



@app.route('/api/scoring', methods=['POST'])
def scoring():
    req = request.json
    user_id = get_user_id(request)
    if user_id is None:
        return jsonify({
            "status": 401,
            "success": False,
            "message": "로그인이 필요합니다"
        })

    quizes = req['quiz_list']

    data = {}
    data['correct_list'] = []

    correct_num = 0#정답 수
    for quiz in quizes:
        result = app.database.execute(text("""
        SELECT
            quiz_content,
            correct_answer,
            correct,
            quiz_type
        FROM Quiz
        WHERE quiz_id = :quiz_id 
        """), quiz).fetchone()#퀴즈 내용과 정답
        req['quiz_type'] = result['quiz_type']
        '''
        if result[2] is not None:
            return jsonify({
                "status": 400,
                "success": False,
                "message": "이미 제출한 퀴즈입니다"
            })            
        '''
        #채점
        q = {}
        q['quiz_id'] = quiz['quiz_id']
        q['content'] = result[0]
        if quiz['my_answer'] == result[1]:
            q['correct'] = 'O'
            quiz['correct'] = True
            correct_num += 1
        else:
            q['correct'] = 'X'
            quiz['correct'] = False


        app.database.execute(text("""
        UPDATE Quiz
        SET
            my_answer = :my_answer,
            correct = :correct
        WHERE quiz_id = :quiz_id
        """), quiz)
        #quiz의 correct update
        data['correct_list'].append(q)#return data에 추가

    data['score'] = str(correct_num) + '/' + str(len(quizes))

    scoreInfo = {}
    scoreInfo['user_id'] = user_id
    scoreInfo['summary_id'] = req['summary_id']
    scoreInfo['quiz_type'] = req['quiz_type']
    scoreInfo['score'] = data['score']

    app.database.execute(text("""
    INSERT INTO Score(
        user_id, 
        summary_id, 
        score,
        quiz_type
    ) VALUES (
        :user_id,
        :summary_id,
        :score,
        :quiz_type
    )
    """), scoreInfo)#score db에 삽입

    return jsonify({
        "status": 200,
        "success": True,
        "message": "퀴즈를 채점합니다",
        "data": data
    })

@app.route('/api/mypagequiz')
def mypagequiz():
    data = {}
    user_id = get_user_id(request)
    if user_id is None:
        return jsonify({
            "status": 401,
            "success": False,
            "message": "로그인이 필요합니다"
        })

    results = app.database.execute(text("""
        SELECT
            *
        FROM Quiz
        WHERE user_id = :user_id 
    """), {'user_id': user_id}).fetchall()#유저의 모든 퀴즈를 가져옴

    quiz_list = []
    quizes = []
    last_index = results[0][5]#마지막으로 처리된 퀴즈의 summary_id
    last_quiz_id = results[-1][0]#불러온 마지막 quiz
    for result in results:
        quiz = {}
        quiz['quiz_id'] = result[0]
        quiz['quiz_content'] = result[2]
        quiz['my_answer'] = result[7]
        quiz['correct_answer'] = result[8]
        quiz['correct'] = result[9]
        if result[9] == 0:
            quiz['correct'] = 'X'
        elif result[9] == 1:
            quiz['correct'] = 'O'

        #정보 저장

        if quiz['quiz_id'] == last_quiz_id:
            quizes.append(quiz)
            dt = {}
            dt['quiz'] = []
            for i in quizes:
                dt['quiz'].append(i)
            dt['quiz_type'] = result[1]
            dt['quiz_date'] = result[3]
            dt['summary_id'] = result[5]
            dt['book_title'] = result[6]

            score = app.database.execute(text("""
            SELECT
                score
            FROM Score
            WHERE summary_id = :summary_id 
            """), dt).fetchone()#스코어
            if score is None:
                dt['score'] = "미제출"
            else:
                dt['score'] = score[0]          
            quiz_list.append(dt)
            quizes.clear()
            #마지막 퀴즈인 경우
    
        elif last_index != result[5]:
            dt = {}
            dt['quiz'] = []
            for i in quizes:
                dt['quiz'].append(i)
            dt['summary_id'] = last_index
            dt['quiz_type'] = result[1]
            dt['quiz_date'] = result[3]
            dt['book_title'] = result[6]
            score = app.database.execute(text("""
            SELECT
                score
            FROM Score
            WHERE summary_id = :summary_id 
            """), dt).fetchone()#스코어
            if score is None:
                dt['score'] = "미제출"
            else:
                dt['score'] = score[0]
            quiz_list.append(dt)
            quizes.clear()
            last_index = result[5]
            #summary_id가 바뀐 경우, 새로운 summary에 대한 quiz

        if quiz['quiz_id'] != last_quiz_id: quizes.append(quiz)

    data['quiz_list'] = quiz_list
    data['user_id'] = user_id
    
    return jsonify({
        "status": 200,
        "success": True,
        "message": "사용자의 퀴즈를 가져옵니다",
        "data": data
    })

@app.route('/api/userSummary')
def userSummary():
    data = {}
    user_id = get_user_id(request)
    if user_id is None:
        return jsonify({
            "status": 401,
            "success": False,
            "message": "로그인이 필요합니다"
        })

    summary_arr = []
    results = app.database.execute(text("""
        SELECT
            *
        FROM Summary
        WHERE user_id = :user_id 
    """), {'user_id': user_id}).fetchall()#user_id에 일치하는 모든 summary
    data['user_id'] = user_id

    for result in results:
        summary = {}
        summary['summary_id'] = result[0]
        summary['summary_title'] = result[2]
        summary['content'] = result[4]
        summary['book_title'] = result[7]
        summary['book_author'] = result[8]
        summary_arr.append(summary)

    data['summary_result'] = summary_arr
    
    return jsonify({
        "status": 200,
        "success": True,
        "message": "사용자 요약 보여주기",
        "data": data
    })


@app.route('/api/allSummary')
def allSummary():
    data = {}
    summary_arr = []
    results = app.database.execute(text("""
        SELECT
            *
        FROM Summary
    """)).fetchall()#모든 summary
    for result in results:
        summary = {}
        summary['summary_id'] = result[0]
        summary['summary_title'] = result[2]
        summary['content'] = result[4]
        summary['book_title'] = result[7]
        summary['book_author'] = result[8]

        user_id = result[1]
        user_name = app.database.execute(text("""
            SELECT
                name
            FROM User
            WHERE user_id = :user_id 
        """), {'user_id': user_id}).fetchone()#user_id에 일치하는 모든 summary
        summary['user_name'] = user_name[0]
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
    if user_id is None:
        return jsonify({
            "status": 401,
            "success": False,
            "message": "로그인이 필요합니다"
        })

    summary_id = request.args.get('summary_id')
    question = request.args.get('question')

    result = app.database.execute(text("""
        SELECT
            bf_summary
        FROM Summary
        WHERE summary_id = :summary_id
    """), {'summary_id': summary_id}).fetchone()
    bf_summary = result[0]

    answer, confidence = ai_qna(bf_summary, question)
    data = {}
    data['answer'] = answer
    data['confidence'] = confidence

    return jsonify({
            "status": 200,
            "success": True,
            "message": "질의응답 성공",
            "data": data
        })


@app.route('/api/review_quiz', methods=['GET'])
def review_quiz_return():
    quiz_type = request.args.get('quiz_type')
    summary_id = request.args.get('summary_id')

    data = {}
    data['quiz_list'] = []

    id = app.database.execute(text("""
        SELECT
            user_id
        FROM Quiz
        WHERE summary_id = :summary_id
    """), {'summary_id': summary_id}).fetchall()#요청된 summary의 user_id

    user_id = get_user_id(request)#요청자의 user_id

    '''
    if user_id != id:
        return jsonify({
            "status": 401,
            "success": False,
            "message": "권한이 없습니다"
        })#두 아이디가 일치하지 않을 경우 권한 없음
    '''

    results = app.database.execute(text("""
        SELECT
            quiz_id,
            quiz_content
        FROM Quiz
        WHERE quiz_type = :quiz_type 
        and summary_id = :summary_id
        and correct = false
    """), {'quiz_type': quiz_type, 'summary_id': summary_id}).fetchall()#요청 summary에 해당하는 quiz list
    
    for result in results:
        quiz = {}
        quiz['quiz_id'] = result[0]
        quiz['content'] = result[1]
        data['quiz_list'].append(quiz)
        #quiz list를 json 배열로 변환


    return jsonify({
        "status": 200,
        "success": True,
        "message": "오답노트 퀴즈를 가져옵니다",
        "data": data
    })


@app.route('/api/review_scoring', methods=['POST'])
def review_scoring():
    req = request.json
    user_id = get_user_id(request)
    if user_id is None:
        return jsonify({
            "status": 401,
            "success": False,
            "message": "로그인이 필요합니다"
        })

    quizes = req['quiz_list']

    data = {}
    data['correct_list'] = []
    review_date = dt.datetime.now()
    correct_num = 0#정답 수
    for quiz in quizes:
        result = app.database.execute(text("""
        SELECT
            quiz_content,
            correct_answer,
            review_correct,
            quiz_type
        FROM Quiz
        WHERE quiz_id = :quiz_id 
        """), quiz).fetchone()#퀴즈 내용과 정답
        req['quiz_type'] = result['quiz_type']
        '''
        if result[2] is not None:
            return jsonify({
                "status": 400,
                "success": False,
                "message": "이미 제출한 퀴즈입니다"
            })            
        '''
        #채점
        q = {}
        q['quiz_id'] = quiz['quiz_id']
        q['content'] = result[0]
        quiz['review_date'] = review_date
        if quiz['review_answer'] == result[1]:
            q['review_correct'] = 'O'
            quiz['review_correct'] = True
            correct_num += 1
        else:
            q['review_correct'] = 'X'
            quiz['review_correct'] = False


        app.database.execute(text("""
        UPDATE Quiz
        SET
            review_answer = :review_answer,
            review_correct = :review_correct,
            review_date = :review_date
        WHERE quiz_id = :quiz_id
        """), quiz)
        #quiz의 correct update
        data['correct_list'].append(q)#return data에 추가

    data['review_score'] = str(correct_num) + '/' + str(len(quizes))

    scoreInfo = {}
    scoreInfo['summary_id'] = req['summary_id']
    scoreInfo['quiz_type'] = req['quiz_type']
    scoreInfo['review_score'] = data['review_score']

    app.database.execute(text("""
    UPDATE Score
    SET
        review_score = :review_score
    Where summary_id = :summary_id
    and quiz_type = :quiz_type
    """), scoreInfo)#score db에 삽입

    return jsonify({
        "status": 200,
        "success": True,
        "message": "오답노트 퀴즈를 채점합니다",
        "data": data
    })


@app.route('/api/reviewquiz')
def reviewquiz():
    data = {}
    user_id = get_user_id(request)
    if user_id is None:
        return jsonify({
            "status": 401,
            "success": False,
            "message": "로그인이 필요합니다"
        })

    results = app.database.execute(text("""
        SELECT
            *
        FROM Quiz
        WHERE user_id = :user_id
        and correct = false
    """), {'user_id': user_id}).fetchall()#유저의 모든 오답노트 퀴즈를 가져옴

    quiz_list = []
    quizes = []
    last_index = results[0][5]#마지막으로 처리된 퀴즈의 summary_id
    last_quiz_id = results[-1][0]#불러온 마지막 quiz
    for result in results:
        quiz = {}
        quiz['quiz_id'] = result[0]
        quiz['quiz_content'] = result[2]
        quiz['correct_answer'] = result[8]
        quiz['review_answer'] = result[10]
        quiz['review_correct'] = result[11]
        if result[11] == 0:
            quiz['review_correct'] = 'X'
        elif result[11] == 1:
            quiz['review_correct'] = 'O'

        #정보 저장

        if quiz['quiz_id'] == last_quiz_id:
            quizes.append(quiz)
            dt = {}
            dt['quiz'] = []
            for i in quizes:
                dt['quiz'].append(i)
            dt['quiz_type'] = result[1]
            dt['quiz_date'] = result[3]
            dt['summary_id'] = result[5]
            dt['book_title'] = result[6]

            score = app.database.execute(text("""
            SELECT
                review_score
            FROM Score
            WHERE summary_id = :summary_id
            and quiz_type = :quiz_type
            """), dt).fetchone()#스코어
            if score is None:
                dt['review_score'] = "미제출"
            else:
                dt['review_score'] = score[0]          
            quiz_list.append(dt)
            quizes.clear()
            #마지막 퀴즈인 경우
    
        elif last_index != result[5]:
            dt = {}
            dt['quiz'] = []
            for i in quizes:
                dt['quiz'].append(i)
            dt['summary_id'] = last_index
            dt['quiz_type'] = result[1]
            dt['quiz_date'] = result[3]
            dt['book_title'] = result[6]
            score = app.database.execute(text("""
            SELECT
                review_score
            FROM Score
            WHERE summary_id = :summary_id 
            """), dt).fetchone()#스코어
            if score is None:
                dt['score'] = "미제출"
            else:
                dt['score'] = score[0]
            quiz_list.append(dt)
            quizes.clear()
            last_index = result[5]
            #summary_id가 바뀐 경우, 새로운 summary에 대한 quiz

        if quiz['quiz_id'] != last_quiz_id: quizes.append(quiz)

    data['quiz_list'] = quiz_list
    data['user_id'] = user_id
    
    return jsonify({
        "status": 200,
        "success": True,
        "message": "사용자의 퀴즈를 가져옵니다",
        "data": data
    })


if __name__ == "__main__":
    #ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    #ssl_context.load_cert_chain(certfile='private.pem', keyfile='private.pem', password='ewha2020summar')
    app.run(host="0.0.0.0", port="5000", ssl_context='adhoc')
