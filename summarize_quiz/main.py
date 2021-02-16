from summarize import total, make_summary
from sqlalchemy import create_engine, text

import json
from flask import Flask, request, g, abort, jsonify
from werkzeug.exceptions import HTTPException, NotFound


app = Flask(__name__)
app.config.from_pyfile("config.py")

database = create_engine(
    app.config['DB_URL'], encoding='utf-8', max_overflow=0)
app.database = database

'''
text = """우리는 많은 시간 인터넷을 이용하고 있지만, 이는 인터넷 회선을 통해 인터넷 서비스를 이용하는 것일 뿐, 내 컴퓨터 안의 파일이 인터넷에 연결되어 있는 것은 아닙니다. HTML로 웹사이트를 만들고 그 내용을 다른 사람들이 볼 수 있도록 하려면 HTML로 만든 웹 문서를 모두 서버 컴퓨터로 옮겨야 합니다. 서버(server)컴퓨터란 전용선을 통해 인터넷에 직접 연결되어 있는 컴퓨터를 가리키는데, 24시간 인터넷에 연결되어있고 서버 컴퓨터 접속 주소만 알면 누구나 서버 컴퓨터의 내용을 볼 수 있습니다. 
인터넷 회선을 통해 서버 컴퓨터에 접속하는 사용자 컴퓨터를 클라이언트(client)컴퓨터라고 합니다. 서버 정보를 가져와 보여주는 것은 사용자 컴퓨터 안의 웹 브라우저이기 때문에 좁은 의미로 웹브라우저를 클라이언트라고도 합니다. 
웹 디자이너나 웹 개발자들은 자신이 제작한 최신 웹사이트를 항상 서버 컴퓨터에 업로드해 놓기 때문에 사용자들은 자신의 위치에 상관없이 어디에서나 인터넷에 접속해서 해당 웹사이트의 내용을 볼 수 있습니다. 
개인은 웹 서버를 마련하기 어렵기 때문에 서버의 일부 공간을 매달 혹은 몇 년마다 일정 금액을 내고 사용하는 서비스를 이용합니다. 이것을 '서버 호스팅 서비스' 혹은 '웹 호스팅 서비스'라고 하는데, 개인 웹사이트를 운영하는 사람들은 대부분 이런 호스팅 서비스를 이용합니다.
호스팅 서비스는 어떤 서버를 이용하느냐에 따라 윈도우 서버 호스팅과 리눅스 서버 호스팅으로 나뉘는데, 윈도우 서버에서는 ASP나 ASAP.NET 프로그래밍 언어를 사용하고, 리눅스 서버에서는 PHP 프로그래밍 언어를 사용하며 좀 더 대중적이고 저렴합니다."""
'''

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


def query_db(query, args=(), one=False):
    cur = app.database.execute(text(query), args)
    rv = [
        dict((cur.description[idx][0], value) for idx, value in enumerate(row))
        for row in cur.fetchall()
    ]
    #cursor fetch 후 row에 하나씩 넣어줌. 그 row를 enumerate 돌려서 idx, value로 dict를 만듦
    return (rv[0] if rv else None) if one else rv

@app.route("/")
def index():
    return "Hello World"


@app.route("/summary", methods=['POST'])
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
        summary_user, question_arr, result_arr = total(bf_summary, count, input_type)
        req['af_summary'] = summary_user
        req['user_id'] = user_id
        #error 없는 상황
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
            
            # summary_id 를 가져오는 부분, 가장 최근에 수행된 AUTO INCREMENT 값을 반환
            sql = "SELECT LAST_INSERT_ID()"
            summary_id = app.database.execute(sql).fetchone()  # 하나만 가져옴

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

#여기까지 완성, 테스트 완료


@app.route('/summary/<summary_id>', methods=['GET'])
def summary_return(summary_id):
    data = {}
    sql = "SELECT af_summary FROM Summary WHERE summary_id = ?"  # summary_id에 따라
    data['content'] = app.database.execute(sql).fetchone()
    data['summary_id'] = summary_id

    response = {}
    response['status'] = 200
    response['success'] = True
    response['message'] = "요약을 반환합니다"
    response['data'] = data

    return jsonify(response)


@app.route('/<quiz_type>/<summary_id>', methods=['GET'])
def quiz_return(quiz_type, summary_id):
    data = {}
    response = {}
    data['quiz_list'] = []
    # query_db 실행 후 저장
    sql = "SELECT quiz_id, quiz_content FROM Quiz WHERE quiz_type = ? and summary_id = ?"
    result = query_db(sql, [quiz_type, summary_id])
    data['quiz_list'] = result
    response['status'] = 200
    response['success'] = True
    response['message'] = "퀴즈를 가져옵니다"
    response['data'] = data

    return jsonify(response)


@app.route('/scoring', methods=['POST'])
def scoring():
    user_id = 'gg'
    quizes = request.form['quiz_list']
    data = {}
    data['correct_list'] = []
    response = {}
    correct_num = 0
    for quiz in quizes:
        # query_db 실행 후 저장
        sql = "SELECT quiz_content, correct_answer FROM Quiz WHERE quiz.quiz_id = ?"
        result = app.database.execute(sql, [quiz.quiz_id]).fetchone()
        q = {}
        q['quiz_id'] = quiz.quiz_id
        q['content'] = result['content']
        if quiz.my_answer == result['correct_answer']:
            q['correct'] = True
            correct_num += 1
        else:
            q['correct'] = False
        data['correct_list'].append(q)

    response['status'] = 200
    response['success'] = True
    response['message'] = "퀴즈를 채점합니다"
    response['data'] = data
    response['score'] = str(correct_num) + '/' + str(len(quizes))

    sql = "INSERT INTO Score (user_id, summary_id, score) VALUES (?, ?, ?)"
    app.database.execute(sql, [
        user_id, request.form['summary_id'], response['score']
    ])
    # g.db.commit()

    return jsonify(response)


@app.route('/userSummary')
def userSummary():
    response = {}
    data = {}
    user_id = "aa"
    summary_r = []
    sql = "SELECT * FROM Summary WHERE user_id = ?"  # query_db 실행 후 저장
    results = query_db(sql, [user_id])
    data['user_id'] = user_id
    for result in results:
        summary = {}
        summary['summary_id'] = result['summary_id']
        summary['summary_title'] = result['summary_title']
        summary['content'] = result['af_summary']
        summary['book_title'] = result['book_title']
        summary['book_author'] = result['book_author']
        summary_r.append(summary)

    response['status'] = 200
    response['success'] = True
    response['message'] = "사용자 요약 보여주기"
    data['summary_result'] = summary_r
    response['data'] = data

    return jsonify(response)


if __name__ == "__main__":
    app.run()
