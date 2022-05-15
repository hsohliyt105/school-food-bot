# -*- coding: utf-8 -*-

provinces = { #17개, 자치시/도와 시도교육청코드
    '서울특별시' : 'B10', 
    '부산광역시' : 'C10', 
    '대구광역시' : 'D10', 
    '인천광역시' : 'E10', 
    '광주광역시' : 'F10', 
    '대전광역시' : 'G10', 
    '울산광역시' : 'H10', 
    '세종특별자치시' : 'I10', 
    '경기도' : 'J10', 
    '강원도' : 'K10', 
    '충청북도' : 'M10', 
    '충청남도' : 'N10', 
    '전라북도' : 'P10', 
    '전라남도' : 'Q10', 
    '경상북도' : 'R10', 
    '경상남도' : 'S10', 
    '제주특별자치도' : 'T10'
    }

command_list = [ '도움말', '오늘급식', '내일급식', '이번주급식', '다음주급식', '이번달급식', '다음달급식', '등록', '삭제', '구독' ]

int_to_day = [ '일', '월', '화', '수', '목', '금', '토' ]

waiting_time = 30 #in seconds

tip_list = ["!등록을 사용하면 학교를 검색할 필요 없이 바로 급식 정보표를 불러올 수 있어요! ", 
            "!이번달급식, !다음달급식을 사용하면 이번 달이나 다음 달의 급식을 이미지로 한꺼번에 볼 수 있습니다. ", 
            "문의사항이나 버그 제보 등은 hsohliyt105@gmail.com으로 보내주시면 감사하겠습니다. ",
            "현재 서버가 임시적인 것으로 인해 상시 양질의 서비스 제공이 안 될 수 있는 점 양해 부탁드립니다. "]

version = "1.1.3"