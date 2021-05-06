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
import nltk

from gaechae import entity

nltk.download('punkt')

okt = Okt()
kovec = Word2Vec.load("D:\ko.bin")
embedding_dim = 200
zero_vector = np.zeros(embedding_dim)
stop_words = ['의', '가', '이', '은', '들', '는', '좀', '잘',
              '걍', '과', '도', '를', '으로', '자', '에', '와', '한', '하다']

data = pd.DataFrame()


def preprocess_sentence(sentence):
    sentence = [re.sub(r'[^가-힣\s]', '', word) for word in sentence]
    return [word for word in sentence if word not in stop_words and word]


def preprocess_sentences(sentences):
    return [preprocess_sentence(sentence) for sentence in sentences]


def tokenization(sentences):
    temp = []
    for sentence in sentences:
        temp_X = okt.morphs(sentence, stem=True)
        temp_X = [word for word in temp_X]
        temp.append(temp_X)
    
    return temp


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


def similarity_matrix(sentence_embedding):
    sim_mat = np.zeros([len(sentence_embedding), len(sentence_embedding)])
    for i in range(len(sentence_embedding)):
        for j in range(len(sentence_embedding)):
            sim_mat[i][j] = cosine_similarity(sentence_embedding[i].reshape(1, embedding_dim),
                                              sentence_embedding[j].reshape(1, embedding_dim))[0, 0]
    return sim_mat


def calculate_score(sim_matrix):
    nx_graph = nx.from_numpy_array(sim_matrix)
    scores = nx.pagerank_numpy(nx_graph)
    return scores


def ranked_sentences(sentences, scores, n):
    top_scores = sorted(((scores[i], s)
                         for i, s in enumerate(sentences)),
                        reverse=True)
    top_n_sentences = [sentence for score, sentence in top_scores[:n]]
    return " ".join(top_n_sentences)


def make_summary(text, count, data):
    data['sentences'] = data['article_text'].apply(sent_tokenize)
    model = Word2Vec(data, sg=1, size=100, window=3, min_count=3, workers=4)
    data['tokenized_data'] = data['sentences'].apply(tokenization)
    data['tokenized_data'] = data['tokenized_data'].apply(preprocess_sentences)
    data['SentenceEmbedding'] = data['tokenized_data'].apply(sentences_to_vectors)
    data['SimMatrix'] = data['SentenceEmbedding'].apply(similarity_matrix)
    data['score'] = data['SimMatrix'].apply(calculate_score)
    data['summary_user'] = data.apply(lambda x:ranked_sentences(x.sentences, x.score, n=count), axis=1)

    data['summary_7'] = data.apply(lambda x: ranked_sentences(x.sentences, x.score, n=7), axis=1)

    return data.loc[0].summary_user  # user summary


# # 문제 만들기
# ### 문장 생성에 쓸 중요 단어 구하기 위한 작업

def list_to_string(tokenized_data):
    tmp = []
    for token_sentence in tokenized_data:
        for token in token_sentence:
            tmp.append(token)
    return tmp


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


def ranked_words(tokenized_data, scores, n=100):
    top_scores = sorted(((scores[i], s)
                         for i, s in enumerate(tokenized_data)),
                        reverse=True)
    top_n_sentences = []
    for score, word in top_scores:
        if word not in top_n_sentences:
            top_n_sentences.append(word)
    return " ".join(top_n_sentences)


# ### 형태소 분석을 이용한 빈칸뚫기
def make_blank(data, type, keyword):
    data['important_word'] = data.apply(lambda x:
                                        ranked_words(x.token, x.word_score), axis=1)
    np.set_printoptions(threshold=sys.maxsize)
    word_set = data['important_word'][0]
    
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
    if type == 0:
        response = http.request(
            "POST",
            openApiURL,
            headers={"Content-Type": "application/json; charset=UTF-8"},
            body=json.dumps(requestJson)
        )
    else:
        response = http.request(
        "POST",
        openApiURL2,
        headers={"Content-Type": "application/json; charset=UTF-8"},
        body=json.dumps(requestJson)
    )
    if str(response.status) == '200':
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
                    if pos == "NNG":
                        result += lemma+" "
                    if pos == "NNP":
                        result += lemma+" "

        # ### 위에서 추린 단어들을 사용자가 입력한 텍스트 전반의 키워드 중심으로 중요도 재배열
        arr = result.split(" ")
        dict = {}
        for word in arr:
            try:
                dict[word] = kovec.wv.similarity(keyword, word)
            except:
                dict[word] = 0
        sdict = sorted(dict.items(), key=operator.itemgetter(1), reverse=True)
        blank_arr = []
        for idx in range(len(sdict)):
            blank_arr.append(sdict[idx][0])
        
        entity_arr = entity(sentence)

        # ### 문제 생성
        question_arr = []
        result_arr = []
        for question in data['summary_sentences'][0]:
            flag = 0
            for word in entity_arr:
                question_tmp = question.replace(word,"*"*len(word))
                if question_tmp != question:
                    question_arr.append(question_tmp)
                    entity_arr.remove(word)
                    result_arr.append(word)
                    if word in blank_arr:
                        blank_arr.remove(word)
                    flag = 1
                    break
            for word in blank_arr:
                if flag == 1:
                    break
                question_tmp = question.replace(word, "*"*len(word))
                if question_tmp != question:
                    question_arr.append(question_tmp)
                    result_arr.append(word)
                    blank_arr.remove(word)
                    break

        return question_arr, result_arr     
    else: 
        return response.status, None
        


def make_quiz(data, type, keyword):
    data['summary_sentences'] = data['summary_7'].apply(sent_tokenize)
    data['tokenized_data_for_word'] = data['summary_sentences'].apply(
        tokenization)
    data['tokenized_data_for_word'] = data['tokenized_data_for_word'].apply(
        preprocess_sentences)
    data['token'] = data['tokenized_data_for_word'].apply(list_to_string)
    data['word_value'] = data['token'].apply(words_to_vectors)
    data['SimMatrix_word'] = data['word_value'].apply(similarity_matrix)
    data['word_score'] = data['SimMatrix_word'].apply(calculate_score)
    question_arr, result_arr = make_blank(data, type, keyword)
    return question_arr, result_arr


def total(text, count, type, keyword):
    data = pd.DataFrame({"article_text": [text]})
    make_summary(text, count, data)
    question_arr, result_arr = make_quiz(data, type, keyword)

    return data.loc[0].summary_user, question_arr, result_arr
