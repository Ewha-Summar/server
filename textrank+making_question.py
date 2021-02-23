#!/usr/bin/env python
# coding: utf-8

# ### 필요 라이브러리 import
from konlpy.tag import Okt
import operator
import pandas as pd
import matplotlib.pyplot as plt
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords  # 불용어
import zipfile
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
import numpy as np
import gensim
from gensim.models.word2vec import Word2Vec
from gensim.test.utils import common_texts
from urllib.request import urlretrieve, urlopen
import gzip
import re
import urllib3
import json
import requests
import sys

# ### 파일 불러오기

#-*- coding: utf-8 -*-
#data = pd.read_csv("D:/test.csv", engine='python')
text = """우리는 많은 시간 인터넷을 이용하고 있지만, 이는 인터넷 회선을 통해 인터넷 서비스를 이용하는 것일 뿐, 내 컴퓨터 안의 파일이 인터넷에 연결되어 있는 것은 아닙니다. HTML로 웹사이트를 만들고 그 내용을 다른 사람들이 볼 수 있도록 하려면 HTML로 만든 웹 문서를 모두 서버 컴퓨터로 옮겨야 합니다. 서버(server)컴퓨터란 전용선을 통해 인터넷에 직접 연결되어 있는 컴퓨터를 가리키는데, 24시간 인터넷에 연결되어있고 서버 컴퓨터 접속 주소만 알면 누구나 서버 컴퓨터의 내용을 볼 수 있습니다. 
        인터넷 회선을 통해 서버 컴퓨터에 접속하는 사용자 컴퓨터를 클라이언트(client)컴퓨터라고 합니다. 서버 정보를 가져와 보여주는 것은 사용자 컴퓨터 안의 웹 브라우저이기 때문에 좁은 의미로 웹브라우저를 클라이언트라고도 합니다. 
웹 디자이너나 웹 개발자들은 자신이 제작한 최신 웹사이트를 항상 서버 컴퓨터에 업로드해 놓기 때문에 사용자들은 자신의 위치에 상관없이 어디에서나 인터넷에 접속해서 해당 웹사이트의 내용을 볼 수 있습니다. 
개인은 웹 서버를 마련하기 어렵기 때문에 서버의 일부 공간을 매달 혹은 몇 년마다 일정 금액을 내고 사용하는 서비스를 이용합니다. 이것을 '서버 호스팅 서비스' 혹은 '웹 호스팅 서비스'라고 하는데, 개인 웹사이트를 운영하는 사람들은 대부분 이런 호스팅 서비스를 이용합니다.
호스팅 서비스는 어떤 서버를 이용하느냐에 따라 윈도우 서버 호스팅과 리눅스 서버 호스팅으로 나뉘는데, 윈도우 서버에서는 ASP나 ASAP.NET 프로그래밍 언어를 사용하고, 리눅스 서버에서는 PHP 프로그래밍 언어를 사용하며 좀 더 대중적이고 저렴합니다.
"""
data= pd.DataFrame({"article_text":[text]})
data.head()


#data = data[['article_text']]
data['sentences'] = data['article_text'].apply(sent_tokenize)
data['sentences'][0]

data


# ### word2vec 파일 가져오기 (더 좋은 파일 있으면 대체하기)

kovec = Word2Vec.load("D:\ko.bin")
#kovec=gensim.models.KeyedVectors.load_word2vec_format('D:\ko.bin',binary=True)

model = Word2Vec(data, sg=1, size=100, window=3, min_count=3, workers=4)


# ### 불용어 추가 및 전처리

stop_words = ['의', '가', '이', '은', '들', '는', '좀', '잘',
              '걍', '과', '도', '를', '으로', '자', '에', '와', '한', '하다']


def preprocess_sentence(sentence):
    sentence = [re.sub(r'[^가-힣\s]', '', word) for word in sentence]
    return [word for word in sentence if word not in stop_words and word]


def preprocess_sentences(sentences):
    return [preprocess_sentence(sentence) for sentence in sentences]
#a-zA-Z, 즉 영어는 포함 안되게 했음


## 형태소 단위로 Tokenize            
okt = Okt()


def tokenization(sentences):
    temp = []
    for sentence in sentences:
        temp_X = okt.morphs(sentence, stem=True)
        temp_X = [word for word in temp_X]
        temp.append(temp_X)
    return temp


data['tokenized_data'] = data['sentences'].apply(tokenization)

data['tokenized_data'] = data['tokenized_data'].apply(preprocess_sentences)

print(data)


embedding_dim = 200
zero_vector = np.zeros(embedding_dim)


# ### 문장별 벡터값 구하기

def calculate_sentence_vector(sentence):
    if len(sentence) != 0:
        sum = 0
        for word in sentence:
            try:
                sum += kovec.wv[word]
            except Exception:
                sum += zero_vector
        return sum/len(sentence)
    else:
        return zero_vector


def sentences_to_vectors(sentences):
    return [calculate_sentence_vector(sentence) for sentence in sentences]


data['SentenceEmbedding'] = data['tokenized_data'].apply(sentences_to_vectors)
data[['SentenceEmbedding']]


# ### 문장별 유사도 구하기
def similarity_matrix(sentence_embedding):
    sim_mat = np.zeros([len(sentence_embedding), len(sentence_embedding)])
    for i in range(len(sentence_embedding)):
        for j in range(len(sentence_embedding)):
            sim_mat[i][j] = cosine_similarity(sentence_embedding[i].reshape(1, embedding_dim),
                                              sentence_embedding[j].reshape(1, embedding_dim))[0, 0]
    return sim_mat


data['SimMatrix'] = data['SentenceEmbedding'].apply(similarity_matrix)
data['SimMatrix']


# ### 점수 계산
def calculate_score(sim_matrix):
    nx_graph = nx.from_numpy_array(sim_matrix)
    scores = nx.pagerank_numpy(nx_graph)
    return scores


data['score'] = data['SimMatrix'].apply(calculate_score)
data[['SimMatrix', 'score']]

data['score'][0]


def ranked_sentences(sentences, scores, n=7):
    top_scores = sorted(((scores[i], s)
                         for i, s in enumerate(sentences)),
                        reverse=True)
    top_n_sentences = [sentence for score, sentence in top_scores[:n]]
    return " ".join(top_n_sentences)


# ### 요약 결과값 산출
data['summary'] = data.apply(lambda x:
                             ranked_sentences(x.sentences, x.score), axis=1)


for i in range(0, len(data)):
    print(i+1, '번 문서')
    print('원문 : ', data.loc[i].article_text)
    print(' ')
    print('요약 : ', data.loc[i].summary)
    print('')


# # 문제 만들기

# ### 문장 생성에 쓸 중요 단어 구하기 위한 작업

data['summary_sentences'] = data['summary'].apply(sent_tokenize)
data['summary_sentences'][0]

data['tokenized_data_for_word'] = data['summary_sentences'].apply(tokenization)

data['tokenized_data_for_word'] = data['tokenized_data_for_word'].apply(
    preprocess_sentences)


def list_to_string(tokenized_data):
    tmp = []
    for token_sentence in tokenized_data:
        for token in token_sentence:
            tmp.append(token)
    return tmp


data['token'] = data['tokenized_data_for_word'].apply(list_to_string)

data['token']


# ### summary 내의 단어들에 대한 점수 구하기
def calculate_word_vector(word):
    if len(word) != 0:
        sum = 0
        for token in word:
            try:
                sum += kovec.wv[token]
            except Exception:
                sum += zero_vector
        return sum
    else:
        return zero_vector


def words_to_vectors(words):
    return [calculate_word_vector(word) for word in words]


data['word_value'] = data['token'].apply(words_to_vectors)

data['SimMatrix_word'] = data['word_value'].apply(similarity_matrix)

data['word_score'] = data['SimMatrix_word'].apply(calculate_score)


def ranked_words(tokenized_data, scores, n=100):
    top_scores = sorted(((scores[i], s)
                         for i, s in enumerate(tokenized_data)),
                        reverse=True)
    #top_n_sentences=[sentence for score,sentence in top_scores[:n]]
    top_n_sentences = []
    for score, word in top_scores:
        if word not in top_n_sentences:
            top_n_sentences.append(word)
    return " ".join(top_n_sentences)


data['important_word'] = data.apply(lambda x:
                                    ranked_words(x.token, x.word_score), axis=1)
np.set_printoptions(threshold=sys.maxsize)
word_set = data['important_word'][0]


# ### 형태소 분석을 이용한 빈칸뚫기

openApiURL = "http://aiopen.etri.re.kr:8000/WiseNLU"

openApiURL2 = "http://aiopen.etri.re.kr:8000/WiseNLU_spoken"

accessKey = "d4a16891-dd45-4883-a873-777a8fda8787"
analysisCode = "ner"
text = ""

result = ""
text += word_set

requestJson = {
    "access_key": accessKey,
    "argument": {
        "text": text,
        "analysis_code": analysisCode
    }
}

http = urllib3.PoolManager()
response = http.request(
    "POST",
    openApiURL,
    headers={"Content-Type": "application/json; charset=UTF-8"},
    body=json.dumps(requestJson)
)


print("[responseCode] " + str(response.status))
print("[responBody]")


# create json object using string
data_2 = json.loads(str(response.data, "utf-8"))

sentence = data_2['return_object']['sentence']  # get the data of sentences

for s in sentence:
    for w in s['word']:  # for loop : words

        text = w['text']  # the text of word

        text_id = int(w['id'])  # the id of word

        begin = int(w['begin'])  # the beginning index of morphemes in word

        end = int(w['end'])  # the ending index of morphemes in word

        for i in range(begin, end+1):  # for : morphemes

            lemma = s['morp'][i]['lemma']  # morpheme

            pos = s['morp'][i]['type']  # tag
            ''''sys.stdout.write("[")'''
            if pos == "NNG":
                #sys.stdout.write("일반명사")
                sys.stdout.write(lemma+"\n")
                result += lemma+" "
            if pos == "NNP":
                #sys.stdout.write("고유명사")
                sys.stdout.write(lemma+"\n")
                result += lemma+" "

print()


# ### 위에서 추린 단어들을 사용자가 입력한 텍스트 전반의 키워드 중심으로 중요도 재배열

kovec = Word2Vec.load("D:\ko.bin")
print(type(kovec))
arr = result.split(" ")
dict = {}

for word in arr:
    try:
        dict[word] = kovec.wv.similarity("범죄", word)
    except:
        dict[word] = 0

sdict = sorted(dict.items(), key=operator.itemgetter(1), reverse=True)
print(sdict)


blank_arr = []
for idx in range(len(sdict)):
    blank_arr.append(sdict[idx][0])

print(blank_arr)


# ### 문제 생성
question_arr = []
result_arr = []
for question in data['summary_sentences'][0]:
    for word in blank_arr:
        question_tmp = question.replace(word, "*"*len(word))
        if question_tmp != question:
            question_arr.append(question_tmp)
            result_arr.append(word)
            break

for idx in range(len(question_arr)):
    print(question_arr[idx]+"\n정답: "+result_arr[idx])
    print()
