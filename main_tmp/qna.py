import urllib3
import json
import requests
import sys

def ai_qna(passage, question):

    openApiURL = "http://aiopen.etri.re.kr:8000/MRCServlet"
    accessKey = "d4a16891-dd45-4883-a873-777a8fda8787"
    
    requestJson = {
        "access_key": accessKey,
        "argument": {
            "question": question,
            "passage": passage
        }
    }
    http = urllib3.PoolManager()
    response = http.request(
        "POST",
        openApiURL,
        headers={"Content-Type": "application/json; charset=UTF-8"},
        body=json.dumps(requestJson)
    )

    data = json.loads(str(response.data,"utf-8"))
    print(data)
    sentence = data['return_object']['MRCInfo']
    answer = sentence['answer']
    confidence = sentence['confidence']

    return answer, confidence