# -*- coding: utf-8 -*-

import os
import time
import json
import asyncio

import requests
from dotenv import load_dotenv
import discord

import helper

load_dotenv(encoding="UTF-8")
EDU_API_KEY = os.getenv("EDU_API_KEY")

def try_get_school(edu_code, school_name):
    """
    학교의 정보를 찾는 함수.

    :param edu_code: string, 시도교육청코드. ATPT_OFCDC_SC_CODE에 해당.
    :param school_name: string, 학교 이름.

    :return: tuple(int 반환코드, list[string] 결과). 
        반환코드: 
            == 0: 실패, 검색 결과가 없음.
            == 1: 성공, 한개를 찾음.
            > 1: 성공, 결과 개수를 표시.
        결과:
            반환코드 == 0일 시: list[], 빈 리스트 반환.
            반환코드 == 1일 시: list[string], 학교 코드 [0]과 학교 이름 [1]을 반환. 
            반환코드 > 1일 시: list[string], 검색 결과에 포함되는 학교 이름을 반환. (최대 10개)
    """

    params = {
                    'KEY': EDU_API_KEY,
                    'pSize': 10,
                    'Type': 'json',
                    'ATPT_OFCDC_SC_CODE': edu_code,
                    'SCHUL_NM': school_name}

    r = requests.get('https://open.neis.go.kr/hub/schoolInfo', params=params)

    try:
        school_data = r.json()['schoolInfo'][1]['row']

    except:
        return (0, [])

    if len(school_data) > 1:
        school_names = []
        for school in school_data:
            school_names.append(school['SCHUL_NM'])

            if school['SCHUL_NM'] == school_name:
                school_code = school_data[0]['SD_SCHUL_CODE']
                return (1, [school_data['SD_SCHUL_CODE'], school['SCHUL_NM']])

        return (len(school_data), school_names)

    if len(school_data) == 1:
        school_code = school_data[0]['SD_SCHUL_CODE']
        return (len(school_data), [school_data[0]['SD_SCHUL_CODE'], school_data[0]['SCHUL_NM']])

    return (0, [])

def get_food_info(edu_code, school_code, start_date, end_date):
    """
    학교의 급식을 찾는 함수.

    :param edu_code: string, 시도교육청코드. ATPT_OFCDC_SC_CODE에 해당.
    :param school_code: string, 학교 코드.
    :param start_date: string, 시작 날짜. YYYYMMDD 형식. 해당 일자 포괄적.
    :param end_date: string, 시작 날짜. YYYYMMDD 형식. 해당 일자 포괄적.

    :return: tuple(int 반환코드, list[dict] 결과). 
        반환코드: 
            == 0: 실패, 검색 결과가 없음.
            > 1: 성공, 결과 개수를 표시.
        결과:
            반환코드 == 0일 시: list[], 빈 리스트 반환.
            반환코드 > 1일 시: list[dict], 급식 리스트 반환.
                dict: 
                    food_name: string, 식단 이름.
                    food_date: string, 식단 날짜.
                    food_info: string, 식단 정보 (식단 목록).
    """

    params = {
                    'KEY': EDU_API_KEY,
                    'Type': 'json',
                    'ATPT_OFCDC_SC_CODE': edu_code,
                    'SD_SCHUL_CODE': school_code,
                    'MLSV_FROM_YMD': str(start_date),
                    'MLSV_TO_YMD': str(end_date)
                    }

    r = requests.get('https://open.neis.go.kr/hub/mealServiceDietInfo', params=params)

    try:
        food_data = r.json()['mealServiceDietInfo'][1]['row']

    except:
        return (0, {})

    food_dicts = []
    for food in food_data:
       food_dicts.append({
            'food_name': food['MMEAL_SC_NM'],
            'food_date': food['MLSV_YMD'],
            'food_info': food['DDISH_NM']
            })

    return (len(food_data), food_dicts)

def get_korean_time(offset_date = 0):
    clock = time.time() + 32400
    cur_time = time.gmtime(clock)

    day = cur_time.tm_mday + offset_date
    mon = cur_time.tm_mon
    year = cur_time.tm_year

    while True:
        if mon == 2:
            if day > 28 and (year % 4 != 0):
                mon += 1
                day -= 28
                continue
            elif day > 29:
                mon += 1
                day -= 29
                continue
        elif mon in [ 4, 6, 9, 11 ]:
            if day > 30:
                mon += 1
                day -= 30
                continue
        else:
            if day > 31:
                mon += 1
                day -= 31
                continue

        if mon > 12:
            year += 1
            mon -= 12
            continue

        break

    str_mon = str(mon)
    str_day = str(day)
    str_year = str(year)

    if day < 10:
        str_day = f'0{str_day}'
    if mon < 10:
        str_mon = f'0{str_mon}'

    str_time = str_year+str_mon+str_day

    return str_time

def get_my_colour(client, channel):
    if isinstance(channel, discord.channel.DMChannel):
        colour = discord.colour.Colour(0)
        return colour

    for member in channel.members:
        if client.user == member:
            colour = member.colour
            return colour

async def try_input_edu(client, message):
    province_list = ""
    for province in helper.provinces.keys():
        province_list += province + "\n"
                
    colour = get_my_colour(client, message.channel)

    embed = discord.Embed(description="자치시/도를 선택해주세요. `예: !경기도`", colour=colour)
    embed.add_field(name="목록", value=province_list)

    edu_list_message = await message.channel.send(embed=embed)
    recent_time = edu_list_message.created_at

    while True:
        messages = await message.channel.history(limit=4, after=recent_time).flatten()
        for mes in messages:
            if mes.content.startswith("!"):
                string = mes.content.split()

                if len(string[0]) > 1:
                    string[0] = string[0][1:]
                    if string[0] in [ "오늘급식", "내일급식", "이번주급식", "다음주급식" ]:
                        break
                else:
                    break

                for province_name in helper.provinces.keys():
                    if province_name in string[0]:
                        await edu_list_message.delete()
                        return helper.provinces[province_name]
        
        await asyncio.sleep(1)

async def try_input_school(client, message, edu_code):
    find_school_message = await message.channel.send("학교를 검색해주세요. `예: !상동초등학교 -> 상동초등학교 ` `예: !상일 -> 상일중학교, 상일고등학교...`")
    find_school_deleted = False
    recent_time = find_school_message.created_at

    while True:
        messages = await message.channel.history(limit=4, after=recent_time).flatten()
        for mes in messages:
            if mes.content.startswith("!"):
                string = mes.content.split()

                if len(string[0]) > 1:
                    string[0] = string[0][1:]
                    if string[0] in [ "오늘급식", "내일급식", "이번주급식", "다음주급식" ]:
                        break
                else:
                    break
                
                school_result = try_get_school(edu_code, string[0])
                if school_result[0] == 0:
                    no_result_message = await message.channel.send("일치하는 검색 결과가 없습니다. ")
                    recent_time = no_result_message.created_at
                    await no_result_message.delete(delay=5)
                    if not find_school_deleted:
                        await find_school_message.delete()
                        find_school_deleted = True
                    break

                if school_result[0] == 1:
                    if not find_school_deleted:
                        await find_school_message.delete()
                        find_school_deleted = True
                    return school_result[1]

                if school_result[0] > 1:
                    school_list = ""
                    for school in school_result[1]:
                        school_list += school + "\n"

                    colour = get_my_colour(client, message.channel)

                    embed = discord.Embed(description="검색결과", colour=colour)
                    embed.add_field(name="목록", value=school_list)

                    list_message = await message.channel.send(embed=embed)
                    recent_time = list_message.created_at
                    await list_message.delete(delay=5)

                    if not find_school_deleted:
                        await find_school_message.delete()
                        find_school_deleted = True

                    break
        
        await asyncio.sleep(1)

def format_food_dict(colour, school_name, date, food_dicts):
    """
    급식 정보를 포맷팅 해주는 함수.

    :param colour: discord.Colour, 자신의 역할 색깔, get_my_colour에서 제공.
    :param school_name: string, 학교 이름.
    :param date: string, 날짜 범위.
    :param food_dicts: tuple(int, dict), get_food_info에서 제공하는 dict를 가져와야함.

    :return: discord.Embed. 
    """

    embed = discord.Embed(title=school_name+" "+date+" 식단", colour=colour)
    for food_dict in food_dicts[1]:
        food_dict['food_info'] = food_dict['food_info'].replace("<br/>", "\n")
        food_dict['food_info'] = food_dict['food_info'].replace("*", "\*")
        embed.add_field(name=food_dict['food_date']+" "+food_dict['food_name'], value=food_dict['food_info'])

    return embed

def to_monday_offset():
    clock = time.time() + 32400
    cur_time = time.gmtime(clock)

    return cur_time.tm_wday