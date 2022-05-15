# -*- coding: utf-8 -*-

import os
import time
import asyncio
import math
import random

import requests
from dotenv import load_dotenv
import discord

import helper
import sql

load_dotenv(encoding="UTF-8")
EDU_API_KEY = os.getenv("EDU_API_KEY")

def try_get_school(edu_code, school_name):
    """
    학교의 정보를 찾는 함수.

    :param edu_code: string, 시도교육청코드. ATPT_OFCDC_SC_CODE에 해당.
    :param school_name: string, 학교 이름.

    :return: list(int 반환코드, list[string] 결과). 
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
        return [ 0, [] ]

    if len(school_data) > 1:
        school_names = []
        for school in school_data:
            school_names.append(school['SCHUL_NM'])

            if school['SCHUL_NM'] == school_name:
                school_code = school_data[0]['SD_SCHUL_CODE']
                return (1, [school_data['SD_SCHUL_CODE'], school['SCHUL_NM']])

        return [ len(school_data), school_names ]

    if len(school_data) == 1:
        school_code = school_data[0]['SD_SCHUL_CODE']
        return [ len(school_data), [school_data[0]['SD_SCHUL_CODE'], school_data[0]['SCHUL_NM']] ]

    return [ 0, [] ]

def get_food_info(edu_code, school_code, start_date, end_date):
    """
    학교의 급식을 찾는 함수.

    :param edu_code: string, 시도교육청코드. ATPT_OFCDC_SC_CODE에 해당.
    :param school_code: string, 학교 코드.
    :param start_date: string, 시작 날짜. YYYYMMDD 형식. 해당 일자 포괄적.
    :param end_date: string, 시작 날짜. YYYYMMDD 형식. 해당 일자 포괄적.

    :return: list(int 반환코드, list[dict] 결과). 
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
                    'MLSV_FROM_YMD': start_date,
                    'MLSV_TO_YMD': end_date
                    }

    r = requests.get('https://open.neis.go.kr/hub/mealServiceDietInfo', params=params)

    try:
        food_data = r.json()['mealServiceDietInfo'][1]['row']

    except:
        return [ 0, {} ]

    food_dicts = []
    for food in food_data:
       food_dicts.append({
            'food_name': food['MMEAL_SC_NM'],
            'food_date': food['MLSV_YMD'],
            'food_info': food['DDISH_NM']
            })

    return [ len(food_data), food_dicts ]

def get_korean_time(offset = 0):
    clock = time.time() + 32400
    cur_time = time.gmtime(clock)

    day = cur_time.tm_mday + offset
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

    embed.set_footer(text=random.choice(helper.tip_list))

    return embed

def to_monday_offset():
    clock = time.time() + 32400
    cur_time = time.gmtime(clock)

    return cur_time.tm_wday

def get_month_ends(offset = 0):
    clock = time.time() + 32400
    cur_time = time.gmtime(clock)

    start_day = 1
    end_day = 0
    mon = cur_time.tm_mon + offset
    year = cur_time.tm_year

    if mon > 12:
        year += 1
        mon -= 12

    if mon == 2:
        end_day = 28
    elif mon in [ 4, 6, 9, 11 ]:
        end_day = 30
    else:
        end_day = 31

    str_start_day = "0" + str(start_day)
    str_end_day = str(end_day)
    str_mon = str(mon)
    str_year = str(year)

    if mon < 10:
        str_mon = f'0{str_mon}'

    str_start_time = str_year+str_mon+str_start_day
    str_end_time = str_year+str_mon+str_end_day

    return str_start_time, str_end_time

def get_day_week(full_date):
    year1 = int(full_date[0:2])
    year2 = int(full_date[2:4])
    month = int(full_date[4:6])
    if month < 3:
        month += 12
    date = int(full_date[6:8])

    return (date + math.floor(13 * (month + 1) / 5) + year2 + math.floor(year2 / 4) + math.floor(year1 / 4) - 2 * year1 - 1) % 7

async def try_input_edu(client, message):
    province_list = ""
    for province in helper.provinces.keys():
        province_list += province + "\n"
                
    colour = get_my_colour(client, message.channel)

    embed = discord.Embed(description="자치시/도를 선택해주세요. `예: !경기도`", colour=colour)
    embed.add_field(name="목록", value=province_list)

    edu_list_message = await message.channel.send(embed=embed)
    await edu_list_message.delete(delay=helper.waiting_time)
    recent_time = edu_list_message.created_at

    while True:
        messages = await message.channel.history(limit=4, after=recent_time).flatten()
        for mes in messages:
            if mes.content.startswith("!"):
                string = mes.content.split()

                if len(string[0]) > 1:
                    string[0] = string[0][1:]
                    if string[0] in helper.command_list:
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
    await find_school_message.delete(delay=helper.waiting_time)
    find_school_deleted = False
    recent_time = find_school_message.created_at

    while True:
        messages = await message.channel.history(limit=4, after=recent_time).flatten()
        for mes in messages:
            if mes.content.startswith("!"):
                string = mes.content.split()

                if len(string[0]) > 1:
                    string[0] = string[0][1:]
                    if string[0] in helper.command_list:
                        break
                else:
                    break
                
                school_result = try_get_school(edu_code, string[0])
                if school_result[0] == 0:
                    no_result_message = await message.channel.send("일치하는 학교 검색 결과가 없습니다. 다시 시도해주세요. ")
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

async def get_user_info(client, message):
    """
    :return: (str)edu_code, (str)school_code, (str)school_name
    """

    edu_code = ""
    school_name = ""
    school_code = ""

    loaded_user = sql.load_user(message.author.id)
    if loaded_user is None:
        try:
            edu_code = await asyncio.wait_for(try_input_edu(client, message), timeout=helper.waiting_time)
        except asyncio.exceptions.CancelledError:
            cancel_message = await message.channel.send(f"{helper.waiting_time}초가 지나 취소되었습니다.")
            await cancel_message.delete(delay=5)
            return

        try:
            school_info = await asyncio.wait_for(try_input_school(client, message, edu_code), timeout=helper.waiting_time)
            school_code = school_info[0]
            school_name = school_info[1]
        except asyncio.exceptions.CancelledError:
            cancel_message = await message.channel.send(f"{helper.waiting_time}초가 지나 취소되었습니다.")
            await cancel_message.delete(delay=5)
            return

    else:
        edu_code = loaded_user['edu_code']
        school_code = loaded_user['school_code']
        school_name = loaded_user['school_name']

    return edu_code, school_code, school_name