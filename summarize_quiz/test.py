from flask import jsonify, Flask, request, session, url_for, redirect, render_template, g, flash, abort
import json
from werkzeug.exceptions import HTTPException, NotFound

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

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
'''


@app.route('/')
def index():
    print("main page")
    return "Hello World"
    '''
    response = {}
    response['status'] = 200
    response['success'] = True
    response['score'] = str(3) + '/' + str(5)

    data = {}
    data['correct_list'] = []
    quiz = {}
    quiz['quiz_id'] = 1
    quiz['content'] = "퀴즈1 내용"
    quiz['correct'] = True
    data['correct_list'].append(quiz)

    response['data'] = data

    return print(jsonify(response))
'''

@app.route('/user')
def user():
    return "user"

if __name__ == "__main__":
    app.run()