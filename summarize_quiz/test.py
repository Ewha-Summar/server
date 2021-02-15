from flask import jsonify

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

#print(jsonify(response))
print(response)