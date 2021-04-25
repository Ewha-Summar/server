def entity(sentence):
    gaechae=[]
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
                tmp=[]
                tmp.append(text)
                if ga=="PS_NAME":
                    tmp.append("사람 이름")
                if ga=="OG_OTHERS":
                    tmp.append("기타 기관/단체")
                if ga=="OGG_ECONOMY":
                    tmp.append("경제 관련 기관")
                if ga=="OGG_EDUCATION":
                    tmp.append("교육 기관")
                if ga=="OGG_MILITARY":
                    tmp.append("군사 기관")
                if ga=="OGG_MEDIA":
                    tmp.append("미디어 기관")
                if ga=="OGG_SPORTS":
                    tmp.append("스포츠 기관")
                if ga=="OGG_ART":
                    tmp.append("예술 기관")
                if ga=="OGG_MEDICINE":
                    tmp.append("의료 기관")
                if ga=="OGG_RELIGION":
                    tmp.append("종교 기관")
                if ga=="OGG_SCIENCE":
                    tmp.append("과학 기관")
                if ga=="OGG_LAW":
                    tmp.append("법률 기관")
                if ga=="OGG_POLITICS":
                    tmp.append("정부/행정 기관")
                if ga=="DT_GEOAGE":
                    tmp.append("지질시대")
                if ga=="DT_DYNASTY":
                    tmp.append("왕조시대")
                if ga=="CV_NAME":
                    tmp.append("문명/문화")
                if ga=="CV_TRIBE":
                    tmp.append("민족/종족")
                if ga=="CV_SPORTS":
                    tmp.append("스포츠")
                if ga=="CV_POLICY":
                    tmp.append("제도/정책")
                if ga=="CV_TAX":
                    tmp.append("조세")
                if ga=="CV_BUILDING_TYPE":
                    tmp.append("건축양식")
                if ga=="CV_POSITION":
                    tmp.append("직위")
                if ga=="CV_OCCUPATION":
                    tmp.append("직업")
                if ga=="CV_CURRENCY":
                    tmp.append("통화")
                if ga=="CV_LAW":
                    tmp.append("법/법률")
                if ga=="AM_INSECT":
                    tmp.append("곤충")
                if ga=="AM_BIRD":
                    tmp.append("조류")
                if ga=="AM_FISH":
                    tmp.append("어류")
                if ga=="AM_MAMMALIA":
                    tmp.append("포유류")
                if ga=="AM_AMPHIBIA":
                    tmp.append("양서류")
                if ga=="AM_REPTILIA":
                    tmp.append("파충류")
                if ga=="AM_TYPE":
                    tmp.append("동물 분류")
                if ga=="PT_OTHERS":
                    tmp.append("기타 식물")
                if ga=="PT_FRUIT":
                    tmp.append("과일")
                if ga=="PT_FLOWER":
                    tmp.append("꽃")
                if ga=="PT_TREE":
                    tmp.append("나무")
                if ga=="PT_GRASS":
                    tmp.append("풀")
                if ga=="PT_TYPE":
                    tmp.append("식물 유형")
                if ga=="PT_PART":
                    tmp.append("식물의 한 부분")
                if ga=="FD_OTHERS":
                    tmp.append("과학 학문")
                if ga=="FD_SCIENCE":
                    tmp.append("사회과학 학문")
                if ga=="FD_SOCIAL_SCIENCE":
                    tmp.append("정치/경제/사회 학문")
                if ga=="FD_MEDICINE":
                    tmp.append("의학 관련 학문")
                if ga=="FD_ART":
                    tmp.append("예술관련 학문")
                if ga=="FD_PHILOSOPHY":
                    tmp.append("철학 관련 학문")
                if ga=="TR_OTHERS":
                    tmp.append("기타이론")
                if ga=="TR_SCIENCE":
                    tmp.append("과학 관련 이론")
                if ga=="TR_SOCIAL_SCIENCE":
                    tmp.append("사회과학 이론")
                if ga=="TR_ART":
                    tmp.append("예술관련 이론")
                if ga=="TR_PHILOSOPHY":
                    tmp.append("철학 이론")
                if ga=="TR_MEDICINE":
                    tmp.append("의학 진단법")
                if ga=="EV_OTHERS":
                    tmp.append("기타 사건")
                if ga=="EV_ACTIVITY":
                    tmp.append("사회운동")
                if ga=="EV_WAR_REVOLUTION":
                    tmp.append("전쟁/혁명")
                if ga=="EV_SPORTS":
                    tmp.append("스포츠/레저")
                if ga=="EV_FESTIVAL":
                    tmp.append("축제")
                if ga=="MT_ELEMENT":
                    tmp.append("원소명")
                if ga=="MT_METAL":
                    tmp.append("금속물")
                if ga=="MT_ROCK":
                    tmp.append("암석")
                if ga=="MT_CHEMICAL":
                    tmp.append("화학물질")
                if ga=="TM_CLIMATE":
                    tmp.append("기후지역")
                if ga=="TM_CELL_TISSUE":
                    tmp.append("세포/조직/기관")
                if ga=="TMM_DISEASE":
                    tmp.append("증세/질병")
                if ga=="TMI_HW":
                    tmp.append("IT 하드웨어")
                if ga=="TMI_SW":
                    tmp.append("IT 소프트웨어")
                if ga=="TMI_MODEL":
                    tmp.append("모델명, 부품류")
                if ga=="TMI_SERVICE":
                    tmp.append("IT 서비스")
                if ga=="TM_SPORTS":
                    tmp.append("스포츠/레저")
                if ga=="AFW_DOCUMENT":
                    tmp.append("서적")
                if ga=="AFW_PERFORMANCE":
                    tmp.append("가극")
                if ga=="AFW_VIDEO":
                    tmp.append("비디오")
                if ga=="AFW_ART_CRAFT":
                    tmp.append("미술작품")
                if ga=="AFW_MUSIC":
                    tmp.append("음악작품")
                if ga=="AF_TRANSPORT":
                    tmp.append("운송수단")
                if ga=="AF_WEAPON":
                    tmp.append("무기")
                if ga=="AF_MUSICAL_INSTRUMENT":
                    tmp.append("악기")
                if ga=="AF_ROAD":
                    tmp.append("도로")
                if ga=="AF_BUILDING":
                    tmp.append("건축물")
                if ga=="AF_CULTURAL_ASSET":
                    tmp.append("문화재")
                if ga=="AF_WORKS":
                    tmp.append("기타작품")
                gaechae.append(tmp)
                if i<end:
                    break

    entity_arr = []
    for word in gaechae:
        if(len(word)==1):
            continue
        else:
            entity_arr.append(word[0])
            
    return entity_arr
            