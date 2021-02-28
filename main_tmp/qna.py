import urllib3
import json
import requests
import sys

def ai_qna(passage, question):

    openApiURL = "http://aiopen.etri.re.kr:8000/WiseNLU" 
    openApiURL2 = "http://aiopen.etri.re.kr:8000/WiseNLU_spoken"
    accessKey = "d4a16891-dd45-4883-a873-777a8fda8787"

    #result=""
    
    requestJson = {
        "access_key": accessKey,
        "argument": {
            "question": question,
            "passage": passage
        }
    }
    print(requestJson)
    print(type(requestJson))

    http = urllib3.PoolManager()
    response = http.request(
        "POST",
        openApiURL,
        headers={"Content-Type": "application/json; charset=UTF-8"},
        body=json.dumps(requestJson)
    )

    #print("[responseCode] " + str(response.status))
    #print("[responBody]")
    #print(str(response.data,"utf-8"))
    #print("\n\n")

    data = json.loads(str(response.data,"utf-8")) # create json object using string

    sentence = data['return_object']['MRCInfo']
    answer = sentence['answer']
    confidence = sentence['confidence']

    return answer, confidence

    '''
    for s in sentence: 
        for w in s['word']: #  for loop : words
            text=w['text'] # the text of word
            text_id=int(w['id']) # the id of word
            begin=int(w['begin']) # the beginning index of morphemes in word
            end=int(w['end']) # the ending index of morphemes in word
        
            for i in range(begin, end+1): # for : morphemes
                lemma=s['morp'][i]['lemma'] # morpheme
                pos=s['morp'][i]['type'] # tag
                sys.stdout.write("[")
                if pos=="NNG":
                    #sys.stdout.write("일반명사")
                    sys.stdout.write(lemma+"\n")
                    result +=lemma+" "
                if pos=="NNP":
                    #sys.stdout.write("고유명사")
                    sys.stdout.write(lemma+"\n")
                    result +=lemma+" "
                if pos=="NNB":
                    sys.stdout.write("의존명사")
                if pos=="NP":
                    sys.stdout.write("대명사")
                if pos=="NR":
                    sys.stdout.write("수사")
                if pos=="VV":
                    sys.stdout.write("동사")
                if pos=="VA":
                    sys.stdout.write("형용사")
                if pos=="VX":
                    sys.stdout.write("보조용언")
                if pos=="VCP":
                    sys.stdout.write("긍정지정사")
                if pos=="VCN":
                    sys.stdout.write("부정지정사")
                if pos=="MM":
                    sys.stdout.write("관형사")
                if pos=="MAG":
                    sys.stdout.write("일반부사")
                if pos=="MAJ":
                    sys.stdout.write("접속부사")
                if pos=="IC":
                    sys.stdout.write("감탄사")
                if pos=="JKS":
                    sys.stdout.write("주격조사")
                if pos=="JKC":
                    sys.stdout.write("보격조사")
                if pos=="JKG":
                    sys.stdout.write("관형격조사")
                if pos=="JKO":
                    sys.stdout.write("목적격조사")
                if pos=="JKB":
                    sys.stdout.write("부사격조사")
                if pos=="JKV":
                    sys.stdout.write("호격조사")
                if pos=="JKQ":
                    sys.stdout.write("인용격조사")
                if pos=="JX":
                    sys.stdout.write("보격조사")
                if pos=="JC":
                    sys.stdout.write("접속조사")
                if pos=="EP":
                    sys.stdout.write("선어말어미")
                if pos=="EF":
                    sys.stdout.write("종결어미")
                if pos=="EC":
                    sys.stdout.write("연결어미")
                if pos=="ETN":
                    sys.stdout.write("명사형전성어미")
                if pos=="ETM":
                    sys.stdout.write("관형형전성어미")
                if pos=="XPN":
                    sys.stdout.write("체언접두사")
                if pos=="XSN":
                    sys.stdout.write("명사파생접미사")
                if pos=="XSV":
                    sys.stdout.write("동사파생접미사")
                if pos=="XSA":
                    sys.stdout.write("형용사파생접미사")
                if pos=="XR":
                    sys.stdout.write("어근")
                if pos=="SF":
                    sys.stdout.write("마침표,물음표,느낌표")
                if pos=="SP":
                    sys.stdout.write("쉼표,가운데점,콜론,빗금")
                if pos=="SS":
                    sys.stdout.write("따옴표,괄호표,줄표")
                if pos=="SE":
                    sys.stdout.write("줄임표")
                if pos=="SO":
                    sys.stdout.write("붙임표")
                if pos=="SL":
                    sys.stdout.write("외국어")
                if pos=="SH":
                    sys.stdout.write("한자")
                if pos=="SW":
                    sys.stdout.write("기타기호")
                if pos=="NF":
                    sys.stdout.write("명사추정범주")
                if pos=="NV":
                    sys.stdout.write("용언추정범주")
                if pos=="SN":
                    sys.stdout.write("숫자")
                if pos=="NA":
                    sys.stdout.write("분석불능범주") 
                sys.stdout.write("]")    
                sys.stdout.write(lemma+"/") # print them
                
                

                if i<end: # print + if the morpheme is not the last one

                    sys.stdout.write(" + ")

            print()

        print()
        

    for s in sentence: 
        t=0
        for w in s['NE']: #  for loop : NE

            text=w['text']; # the text of word

            text_id=int(w['id']); # the id of word

            begin=int(w['begin']) # the beginning index of morphemes in word

            end=int(w['end']) # the ending index of morphemes in word
            
        
            for i in range(begin, end+1): # for : morphemes
                
                ga=s['NE'][t]['type']
                t+=1
                sys.stdout.write(text+" : ")
                
                if ga=="PS_NAME":
                    sys.stdout.write("사람 이름")
                if ga=="LC_OTHERS":
                    sys.stdout.write("기타 장소")
                if ga=="LCP_COUNTRY":
                    sys.stdout.write("국가명")
                if ga=="LCP_PROVINCE":
                    sys.stdout.write("도, 주 지역명")
                if ga=="LCP_COUNTY":
                    sys.stdout.write("세부 행정구역명")
                if ga=="LCP_CITY":
                    sys.stdout.write("도시명")
                if ga=="LCP_CAPITALCITY":
                    sys.stdout.write("수도명")
                if ga=="LCG_RIVER":
                    sys.stdout.write("강")
                if ga=="LCG_OCEAN":
                    sys.stdout.write("바다")
                if ga=="LCG_MOUNTAIN":
                    sys.stdout.write("산")
                if ga=="LCG_CONTINENT":
                    sys.stdout.write("대륙")
                if ga=="LC_SPACE":
                    sys.stdout.write("천체 명칭")
                if ga=="LCG_ISLAND":
                    sys.stdout.write("섬")

                if ga=="OG_OTHERS":
                    sys.stdout.write("기타 기관/단체")
                if ga=="OGG_ECONOMY":
                    sys.stdout.write("경제 관련 기관")
                if ga=="OGG_EDUCATION":
                    sys.stdout.write("교육 기관")
                if ga=="OGG_MILITARY":
                    sys.stdout.write("군사 기관/")
                if ga=="OGG_MEDIA":
                    sys.stdout.write("미디어 기관")
                if ga=="OGG_SPORTS":
                    sys.stdout.write("스포츠 기관")
                if ga=="OGG_ART	":
                    sys.stdout.write("예술 기관")
                if ga=="OGG_MEDICINE":
                    sys.stdout.write("의료 기관")
                if ga=="OGG_RELIGION":
                    sys.stdout.write("종교 기관")
                if ga=="OGG_SCIENCE":
                    sys.stdout.write("과학 기관")
                if ga=="OGG_LIBRARY":
                    sys.stdout.write("도서관")
                if ga=="OGG_LAW":
                    sys.stdout.write("법률 기관")
                if ga=="OGG_POLITICS":
                    sys.stdout.write("정부/행정 기관")
                if ga=="OGG_FOOD":
                    sys.stdout.write("음식 업체")
                if ga=="OGG_HOTEL":
                    sys.stdout.write("숙박 업체")
                if ga=="DT_OTHERS":
                    sys.stdout.write("기타 날짜")
                if ga=="DT_DURATION":
                    sys.stdout.write("기간")
                if ga=="DT_DAY":
                    sys.stdout.write("날짜/절기")
                if ga=="DT_MONTH":
                    sys.stdout.write("달")
                if ga=="DT_YEAR":
                    sys.stdout.write("년")
                if ga=="DT_SEASON":
                    sys.stdout.write("계절")
                if ga=="DT_GEOAGE":
                    sys.stdout.write("지질시대")
                if ga=="DT_DYNASTY":
                    sys.stdout.write("왕조시대")
                if ga=="TI_OTHERS":
                    sys.stdout.write("기타 시간")
                if ga=="TI_DURATION":
                    sys.stdout.write("기간")
                if ga=="TI_HOUR":
                    sys.stdout.write("시각")
                if ga=="TI_MINUTE":
                    sys.stdout.write("분")
                if ga=="TI_SECOND":
                    sys.stdout.write("초")
                if ga=="CV_NAME":
                    sys.stdout.write("문명/문화")
                if ga=="CV_TRIBE":
                    sys.stdout.write("민족/종족")
                if ga=="CV_SPORTS":
                    sys.stdout.write("스포츠")
                if ga=="CV_SPORTS_INST":
                    sys.stdout.write("스포츠 용품")
                if ga=="CV_POLICY":
                    sys.stdout.write("제도/정책")
                if ga=="CV_TAX":
                    sys.stdout.write("조세")
                if ga=="CV_FUNDS":
                    sys.stdout.write("기금")
                if ga=="CV_LANGUAGE":
                    sys.stdout.write("언어")
                if ga=="CV_BUILDING_TYPE":
                    sys.stdout.write("건축양식")
                if ga=="CV_FOOD	":
                    sys.stdout.write("음식")
                if ga=="CV_DRINK":
                    sys.stdout.write("음료수")
                if ga=="CV_CLOTHING":
                    sys.stdout.write("의복")
                if ga=="CV_POSITION":
                    sys.stdout.write("직위")
                if ga=="CV_RELATION":
                    sys.stdout.write("인간 관계")
                if ga=="CV_OCCUPATION":
                    sys.stdout.write("직업")
                if ga=="CV_CURRENCY":
                    sys.stdout.write("통화")
                if ga=="CV_PRIZE":
                    sys.stdout.write("상")
                if ga=="CV_LAW":
                    sys.stdout.write("법/법률")
                if ga=="CV_FOOD_STYLE":
                    sys.stdout.write("음식 종류")
                if ga=="AM_OTHERS":
                    sys.stdout.write("기타 동물")
                if ga=="AM_INSECT":
                    sys.stdout.write("곤충")
                if ga=="AM_BIRD":
                    sys.stdout.write("조류")
                if ga=="AM_FISH":
                    sys.stdout.write("어류")
                if ga=="AM_MAMMALIA":
                    sys.stdout.write("포유류")
                if ga=="AM_AMPHIBIA":
                    sys.stdout.write("양서류")
                if ga=="AM_REPTILIA":
                    sys.stdout.write("파충류")
                if ga=="AM_TYPE":
                    sys.stdout.write("동물 분류")
                if ga=="AM_PART":
                    sys.stdout.write("신체 부위")
                if ga=="PT_OTHERS":
                    sys.stdout.write("기타 식물")
                if ga=="PT_FRUIT":
                    sys.stdout.write("과일")
                if ga=="PT_FLOWER":
                    sys.stdout.write("꽃")
                if ga=="PT_TREE":
                    sys.stdout.write("나무")
                if ga=="PT_GRASS":
                    sys.stdout.write("풀")
                if ga=="PT_TYPE":
                    sys.stdout.write("식물 유형")
                if ga=="PT_PART":
                    sys.stdout.write("식물의 한 부분")

                if ga=="QT_OTHERS":
                    sys.stdout.write("기타 수량")
                if ga=="QT_AGE":
                    sys.stdout.write("나이")
                if ga=="QT_SIZE":
                    sys.stdout.write("크기/넓이")
                if ga=="QT_LENGTH":
                    sys.stdout.write("길이/거리/높이")
                if ga=="QT_COUNT":
                    sys.stdout.write("개수/빈도")
                if ga=="QT_MAN_COUNT":
                    sys.stdout.write("인원수")
                if ga=="QT_WEIGHT":
                    sys.stdout.write("무게")
                if ga=="QT_PERCENTAGE":
                    sys.stdout.write("비율")
                if ga=="QT_SPEED":
                    sys.stdout.write("속도")
                if ga=="QT_TEMPERATURE":
                    sys.stdout.write("")
                if ga=="QT_VOLUME":
                    sys.stdout.write("부피")
                if ga=="QT_ORDER":
                    sys.stdout.write("순서")
                if ga=="QT_PRICE":
                    sys.stdout.write("금액")
                if ga=="QT_PHONE":
                    sys.stdout.write("전화번호")
                if ga=="QT_SPORTS":
                    sys.stdout.write("스포츠 관련 수량")
                if ga=="QT_CHANNEL":
                    sys.stdout.write("채널")
                if ga=="QT_ALBUM":
                    sys.stdout.write("앨범 관련 수량")
                if ga=="QT_ZIPCODE":
                    sys.stdout.write("우편번호")
                if ga=="FD_OTHERS":
                    sys.stdout.write("과학 학문")
                if ga=="FD_SCIENCE":
                    sys.stdout.write("사회과학 학문")
                if ga=="FD_SOCIAL_SCIENCE":
                    sys.stdout.write("정치/경제/사회 학문")
                if ga=="FD_MEDICINE":
                    sys.stdout.write("의학 관련 학문")
                if ga=="FD_ART":
                    sys.stdout.write("예술관련 학문")
                if ga=="FD_PHILOSOPHY":
                    sys.stdout.write("철학 관련 학문")

                if ga=="TR_OTHERS":
                    sys.stdout.write("기타이론")
                if ga=="TR_SCIENCE":
                    sys.stdout.write("과학 관련 이론")
                if ga=="TR_SOCIAL_SCIENCE":
                    sys.stdout.write("사회과학 이론")
                if ga=="TR_ART":
                    sys.stdout.write("예술관련 이론")
                if ga=="TR_PHILOSOPHY":
                    sys.stdout.write("철학 이론")
                if ga=="TR_MEDICINE":
                    sys.stdout.write("의학 진단법")

                if ga=="EV_OTHERS":
                    sys.stdout.write("기타 사건")
                if ga=="EV_ACTIVITY":
                    sys.stdout.write("사회운동")
                if ga=="EV_WAR_REVOLUTION":
                    sys.stdout.write("전쟁/혁명")
                if ga=="EV_SPORTS":
                    sys.stdout.write("스포츠/레저")
                if ga=="EV_FESTIVAL":
                    sys.stdout.write("축제")
                if ga=="MT_ELEMENT":
                    sys.stdout.write("원소명")
                if ga=="MT_METAL":
                    sys.stdout.write("금속물")
                if ga=="MT_ROCK":
                    sys.stdout.write("암석")
                if ga=="MT_CHEMICAL":
                    sys.stdout.write("화학물질")
                if ga=="TM_COLOR":
                    sys.stdout.write("색")
                if ga=="TM_DIRECTION":
                    sys.stdout.write("방향")
                if ga=="TM_CLIMATE":
                    sys.stdout.write("기후지역")
                if ga=="TM_SHAPE":
                    sys.stdout.write("모양/형태")
                if ga=="TM_CELL_TISSUE":
                    sys.stdout.write("세포/조직/기관")
                if ga=="TMM_DISEASE":
                    sys.stdout.write("증세/질병")
                if ga=="TMM_DRUG":
                    sys.stdout.write("약/약품명")
                if ga=="TMI_HW":
                    sys.stdout.write("IT 하드웨어")
                if ga=="TMI_SW":
                    sys.stdout.write("IT 소프트웨어")
                if ga=="TMI_SITE":
                    sys.stdout.write("URL 주소")
                if ga=="TMI_EMAIL":
                    sys.stdout.write("이메일주소")
                if ga=="TMI_MODEL":
                    sys.stdout.write("모델명, 부품류")
                if ga=="TMI_SERVICE":
                    sys.stdout.write("IT 서비스")
                if ga=="TMI_PROJECT":
                    sys.stdout.write("프로젝트")
                if ga=="TMIG_GENRE":
                    sys.stdout.write("게임 장르")
                if ga=="TM_SPORTS":
                    sys.stdout.write("스포츠/레저")
                if ga=="AFW_DOCUMENT":
                    sys.stdout.write("서적")
                if ga=="AFW_PERFORMANCE":
                    sys.stdout.write("가극")
                if ga=="AFW_VIDEO":
                    sys.stdout.write("비디오")
                if ga=="AFW_ART_CRAFT":
                    sys.stdout.write("미술작품")
                if ga=="AFW_MUSIC":
                    sys.stdout.write("음악작품")
                if ga=="AF_WARES":
                    sys.stdout.write("상품")
                if ga=="AF_TRANSPORT":
                    sys.stdout.write("운송수단")
                if ga=="AF_WEAPON":
                    sys.stdout.write("무기")
                if ga=="AF_MUSICAL_INSTRUMENT":
                    sys.stdout.write("악기")
                if ga=="AF_ROAD":
                    sys.stdout.write("도로")
                if ga=="AF_BUILDING":
                    sys.stdout.write("건축물")
                if ga=="AF_CULTURAL_ASSET":
                    sys.stdout.write("문화재")
                if ga=="AF_WORKS":
                    sys.stdout.write("기타작품")
                if i<end:
                    break
            print()
    '''