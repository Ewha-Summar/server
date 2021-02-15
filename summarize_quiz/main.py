from summarize import total, make_summary

import json
from flask import Flask, request, g, abort, jsonify

app = Flask(__name__)


text = """우리는 많은 시간 인터넷을 이용하고 있지만, 이는 인터넷 회선을 통해 인터넷 서비스를 이용하는 것일 뿐, 내 컴퓨터 안의 파일이 인터넷에 연결되어 있는 것은 아닙니다. HTML로 웹사이트를 만들고 그 내용을 다른 사람들이 볼 수 있도록 하려면 HTML로 만든 웹 문서를 모두 서버 컴퓨터로 옮겨야 합니다. 서버(server)컴퓨터란 전용선을 통해 인터넷에 직접 연결되어 있는 컴퓨터를 가리키는데, 24시간 인터넷에 연결되어있고 서버 컴퓨터 접속 주소만 알면 누구나 서버 컴퓨터의 내용을 볼 수 있습니다. 
인터넷 회선을 통해 서버 컴퓨터에 접속하는 사용자 컴퓨터를 클라이언트(client)컴퓨터라고 합니다. 서버 정보를 가져와 보여주는 것은 사용자 컴퓨터 안의 웹 브라우저이기 때문에 좁은 의미로 웹브라우저를 클라이언트라고도 합니다. 
웹 디자이너나 웹 개발자들은 자신이 제작한 최신 웹사이트를 항상 서버 컴퓨터에 업로드해 놓기 때문에 사용자들은 자신의 위치에 상관없이 어디에서나 인터넷에 접속해서 해당 웹사이트의 내용을 볼 수 있습니다. 
개인은 웹 서버를 마련하기 어렵기 때문에 서버의 일부 공간을 매달 혹은 몇 년마다 일정 금액을 내고 사용하는 서비스를 이용합니다. 이것을 '서버 호스팅 서비스' 혹은 '웹 호스팅 서비스'라고 하는데, 개인 웹사이트를 운영하는 사람들은 대부분 이런 호스팅 서비스를 이용합니다.
호스팅 서비스는 어떤 서버를 이용하느냐에 따라 윈도우 서버 호스팅과 리눅스 서버 호스팅으로 나뉘는데, 윈도우 서버에서는 ASP나 ASAP.NET 프로그래밍 언어를 사용하고, 리눅스 서버에서는 PHP 프로그래밍 언어를 사용하며 좀 더 대중적이고 저렴합니다."""


def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [
        dict((cur.description[idx][0], value) for idx, value in enumerate(row))
        for row in cur.fetchall()
    ]
    #cursor fetch 후 row에 하나씩 넣어줌. 그 row를 enumerate 돌려서 idx, value로 dict를 만듦
    return (rv[0] if rv else None) if one else rv



@app.route('/summary', methods=['POST'])
def summary():
    data = {}
    response = {}

    user_id = "aa"
    if request.method == 'POST':
        summary_user, question_arr, result_arr = total(request.form['text'], request.form['count'], request.form['input_type'])#0은 문어체, 1은 구어체

        #error 없는 상황
        if result_arr is not None:
            sql = "INSERT INTO Summary (user_id, summary_title, bf_summary, af_summary, input_type, book_title, book_author) VALUES (?, ?, ?, ?, ?, ?, ?)"
            g.db.execute(sql, [
                user_id, request.form['summary_title'], request.form['text'], summary_user, request.form['input_type'], request.form['book_title'], request.form['book_author']
            ])
            g.db.commit()
            sql = "SELECT LAST_INSERT_ID()" #summary_id 를 가져오는 부분, 가장 최근에 수행된 AUTO INCREMENT 값을 반환
            summary_id = g.db.execute(sql).fetchone()  #하나만 가져옴

            quiz_date = 1/2

            for i in range(len(question_arr)):
                sql = "INSERT INTO Quiz (quiz_type, quiz_content, quiz_date, user_id, summary_id, book_title, correct_answer) VALUES (?, ?, ?, ?, ?, ?, ?)"
                g.db.execute(sql, [
                    request.form['quiz_type'], question_arr[i], quiz_date, user_id, summary_id, request.form['book_title'], result_arr[i]
                ])
                g.db.commit()
            
            response['status'] = 200
            response['success'] = True
            data['content'] = summary_user
            data['summary_id'] = summary_id
            response['data'] = data
        #error 발생 상황
        else:
            response['status'] = question_arr
            response['success'] = False
            response['message'] = "error message"
        return jsonify(response)
        #result_arr가 None인 경우 question_arr에 responseCode가 저장되어 있음

"""
sql문 작성

1) summary db에 삽입.
  `summary_id` INT NOT NULL AUTO_INCREMENT,     -> auto increment
  `user_id` VARCHAR(25) NOT NULL,               -> jwt 토큰에서 얻어옴
  `summary_title` VARCHAR(100) NOT NULL,        -> form에서 받기
  `bf_summary` VARCHAR(5000) NOT NULL,          -> form에서 받기
  `af_summary` VARCHAR(2000) NOT NULL,          -> summary 결과 저장
  `input_type` INT NOT NULL,                    -> form에서 받기
  `book_id` INT NULL,                           -> book_title로 변경해야함. form에서 받기

2) quiz db에 삽입.
 `quiz_id` INT NOT NULL AUTO_INCREMENT,         -> auto increment
  `quiz_type` INT NOT NULL,                     -> 일단은 빈칸문제인듯
  `quiz_content` VARCHAR(1500) NOT NULL,        -> 퀴즈 내용 저장
  `quiz_date` DATE NOT NULL,                    -> 현재 시간?
  `user_id` VARCHAR(25) NOT NULL,               -> jwt 토큰에서 얻어옴
  `summary_id` INT NOT NULL,                    -> 생성된 summary id 에서 얻음
  `book_id` INT NOT NULL,                       -> book_title로 대체
  `my_answer` VARCHAR(500) NULL,                -> null
  `correct_answer` VARCHAR(500) NOT NULL,       -> null
  `correct` BOOLEAN NULL,                       -> null

{
"status" : 200,
"success" : true,
"data" : {
    "input_type" : 0,
    "count" : 3,
    "summary_id" : 4
}
"""



@app.route('/summary/<summary_id>', methods=['GET'])
def summary_return(summary_id):
    data = {}
    sql = "SELECT af_summary FROM Summary WHERE summary_id = ?" #summary_id에 따라 
    data['content'] = g.db.execute(sql).fetchone()
    data['summary_id'] = summary_id

    response = {}
    response['status'] = 200
    response['success'] = True
    response['data'] = data

    """
    "status" : 200,
    "success" : true,
    "data" : {
        "content" : "요약된 문장입니다", // 요약된 문장
        "summary_id" : 4
    }
    """



@app.route('/<quiz_type>/<summary_id>', methods=['GET'])
def quiz_return(quiz_type, summary_id):
    data = {}
    response = {}
    data['quiz_list'] = []
    sql = "SELECT quiz_id, quiz_content FROM Quiz WHERE quiz_type = ? and summary_id = ?" #query_db 실행 후 저장
    result = query_db(sql, [quiz_type, summary_id])
    data['quiz_list'] = result
    response['status'] = 200
    response['success'] = True
    response['data'] = data

    return jsonify(response)
    """
    "status" : 200,
    "success": true,
    "data" : {
        "quiz_list": [ // 퀴즈 배열
        {
            "quiz_id" : 1
            "content" : "퀴즈1 내용입니다"
        },
        {
            "quiz_id" : 2
            "content" : "퀴즈2 내용입니다"
        }
    ]}
    """


@app.route('/scoring', methods=['POST'])
def scoring():
    quizes = request.form['quiz_list']
    data = {}
    data['correct_list'] = []
    response = {}
    correct_num = 0
    for quiz in quizes:
        sql = "SELECT quiz_content, correct_answer FROM Quiz WHERE quiz.quiz_id = ?" #query_db 실행 후 저장
        result = g.db.execute(sql, [quiz.quiz_id]).fetchone()
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
    response['data'] = data
    response['score'] = str(correct_num) + '/' + str(len(quizes))

    return jsonify(response)

    """
    "status": 200
    "success": true,
    "data" : {
        "correct_list": [
            {
                "quiz_id": 1
                "content" : "퀴즈1 내용입니다",
                "correct": true
            },           
            {
                "quiz_id": 3
                "content" : "퀴즈3 내용입니다",
                "correct": false
            }
        ],
    "score" : "1/2"
    """    
