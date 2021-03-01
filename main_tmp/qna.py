import urllib3
import json
import requests
import sys

def ai_qna(passage, question):

    answer = {}
    confidence = {}
    #buffer = passage
    size = len(passage)//1000 # 전체 텍스트를 1000자로 나눴을 때 chunk 개수
    for idx in range(0, size + 1):
        if idx != size:
            split_passage = passage[idx*1000:(idx+1)*1000]
        else:
            split_passage = passage[idx*1000:]
            

        openApiURL = "http://aiopen.etri.re.kr:8000/MRCServlet"
        accessKey = "d4a16891-dd45-4883-a873-777a8fda8787"
        
        requestJson = {
            "access_key": accessKey,
            "argument": {
                "question": question,
                "passage": split_passage
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
        #print(data)
        sentence = data['return_object']['MRCInfo']
        answer[idx] = sentence['answer']
        confidence[idx] = sentence['confidence']

    print(answer)
    print(confidence)
    final_confidence = 0
    final_answer = ""
    for idx2 in range(len(size)):
        if int(float(final_confidence)) < int(float(confidence[idx2])):
            final_confidence = confidence[idx2]
            final_answer = answer[idx2]
    
    print(final_confidence)
    print(final_answer)
    return final_answer, final_confidence