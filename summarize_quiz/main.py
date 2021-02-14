from summarize import total, make_summary

from flask import Flask, request, session, url_for, redirect, render_template, g, flash, abort

app = Flask(__name__)



text = """우리는 많은 시간 인터넷을 이용하고 있지만, 이는 인터넷 회선을 통해 인터넷 서비스를 이용하는 것일 뿐, 내 컴퓨터 안의 파일이 인터넷에 연결되어 있는 것은 아닙니다. HTML로 웹사이트를 만들고 그 내용을 다른 사람들이 볼 수 있도록 하려면 HTML로 만든 웹 문서를 모두 서버 컴퓨터로 옮겨야 합니다. 서버(server)컴퓨터란 전용선을 통해 인터넷에 직접 연결되어 있는 컴퓨터를 가리키는데, 24시간 인터넷에 연결되어있고 서버 컴퓨터 접속 주소만 알면 누구나 서버 컴퓨터의 내용을 볼 수 있습니다. 
인터넷 회선을 통해 서버 컴퓨터에 접속하는 사용자 컴퓨터를 클라이언트(client)컴퓨터라고 합니다. 서버 정보를 가져와 보여주는 것은 사용자 컴퓨터 안의 웹 브라우저이기 때문에 좁은 의미로 웹브라우저를 클라이언트라고도 합니다. 
웹 디자이너나 웹 개발자들은 자신이 제작한 최신 웹사이트를 항상 서버 컴퓨터에 업로드해 놓기 때문에 사용자들은 자신의 위치에 상관없이 어디에서나 인터넷에 접속해서 해당 웹사이트의 내용을 볼 수 있습니다. 
개인은 웹 서버를 마련하기 어렵기 때문에 서버의 일부 공간을 매달 혹은 몇 년마다 일정 금액을 내고 사용하는 서비스를 이용합니다. 이것을 '서버 호스팅 서비스' 혹은 '웹 호스팅 서비스'라고 하는데, 개인 웹사이트를 운영하는 사람들은 대부분 이런 호스팅 서비스를 이용합니다.
호스팅 서비스는 어떤 서버를 이용하느냐에 따라 윈도우 서버 호스팅과 리눅스 서버 호스팅으로 나뉘는데, 윈도우 서버에서는 ASP나 ASAP.NET 프로그래밍 언어를 사용하고, 리눅스 서버에서는 PHP 프로그래밍 언어를 사용하며 좀 더 대중적이고 저렴합니다."""


@app.route('/summary', methods=['POST'])
def summary():
    error = None
    user_id = "aa"
    if request.method == 'POST':
        #summary, question_arr, result_arr = total(text, 3, 0)#0은 문어체, 1은 구어체
        summary_user, question_arr, result_arr = total(request.form['text'], request.form['count'], request.form['input_type'])#0은 문어체, 1은 구어체
        sql = "INSERT INTO Summary (user_id, summary_title, bf_summary, af_summary, input_type, book_title, book_author) VALUES (?, ?, ?, ?, ?, ?, ?)"
        g.db.execute(sql, [
            user_id, request.form['summary_title'], request.form['text'], summary_user, request.form['input_type'], request.form['book_title'], request.form['book_author']
        ])
        g.db.commit()

        if result_arr is not None:
            print(summary_user)
            for i in range(len(question_arr)):
                print(question_arr[i])
                print(result_arr[i])
                #result_arr가 None인 경우 question_arr에 responseCode가 저장되어 있음
        else:
            print(question_arr)
            #error 발생 상황입니다


    #summary_id를 가져오기 위한 부분   ??? 이거 어떻게 가져오지???????? 뭘로 검색해?
    sql = "SELECT user_id FROM user WHERE username = ?"
    rv = g.db.execute(sql, [username]).fetchone()  #하나만 가져옴
    return rv[0] if rv else None




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



api 명세서로 json return
            {
             "status" : 200,
             "success" : true,
             "data" : {
                "input_type" : "0",
                "count" : 3,
                "summary_id" : 4
             }
"""