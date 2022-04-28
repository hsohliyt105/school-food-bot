# -*- coding: utf-8 -*-

import asyncio
import io

import discord

import helper
import functions
import drawer

async def try_input_edu(client, message):
    province_list = ""
    for province in helper.provinces.keys():
        province_list += province + "\n"
                
    colour = functions.get_my_colour(client, message.channel)

    embed = discord.Embed(description="자치시/도를 선택해주세요. `예: !경기도`", colour=colour)
    embed.add_field(name="목록", value=province_list)

    edu_list_message = await message.channel.send(embed=embed)
    await edu_list_message.delete(delay=10)
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
    await find_school_message.delete(delay=30)
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
                
                school_result = functions.try_get_school(edu_code, string[0])
                if school_result[0] == 0:
                    no_result_message = await message.channel.send("일치하는 학교 검색 결과가 없습니다. ")
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

                    colour = functions.get_my_colour(client, message.channel)

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

async def try_input_food_type(message, food_types):
    input_type_text = "식단 종류가 너무 많습니다. 종류를 선택해주세요: "

    for food_type in food_types:
        input_type_text += f"`!{food_type}`, "

    input_type_text = input_type_text[:-2]

    input_type_message = await message.channel.send(input_type_text)
    await input_type_message.delete(delay=30)
    input_type_deleted = False
    recent_time = input_type_message.created_at

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
                
                if string[0] in food_types:
                    chosen_food_type = string[0]
                    await input_type_message.delete()
                    return chosen_food_type
        
        await asyncio.sleep(1)

async def help_message(message):
    command_list_text = f"`{'`, `'.join(helper.command_list)}`"

    embed = discord.Embed(title="명령어 목록", description=command_list_text)

    await message.channel.send(embed=embed)

    return

async def food_message(client, message, start_offset, end_offset):
    try:
        edu_code = await asyncio.wait_for(try_input_edu(client, message), timeout=10)
    except:
        cancel_message = await message.channel.send("10초가 지나 취소되었습니다.")
        await cancel_message.delete(delay=5)
        return

    try:
        school_info = await asyncio.wait_for(try_input_school(client, message, edu_code), timeout=30)
    except:
        cancel_message = await message.channel.send("30초가 지나 취소되었습니다.")
        await cancel_message.delete(delay=5)
        return
            
    school_code = school_info[0]
    school_name = school_info[1]

    if start_offset == end_offset:
        date = functions.get_korean_time(start_offset)
        date_text = date
        food_dicts = functions.get_food_info(edu_code, school_code, date, date)

    else:
        offset = functions.to_monday_offset()
        mon_date = functions.get_korean_time(-offset + start_offset)
        sun_date = functions.get_korean_time(-offset + end_offset)
        date_text = f"{mon_date}-{sun_date}"
        food_dicts = functions.get_food_info(edu_code, school_code, mon_date, sun_date)

    if food_dicts[0] == 0:
        await message.channel.send("급식 결과가 없습니다.")
        return

    colour = functions.get_my_colour(client, message.channel)

    embed = functions.format_food_dict(colour, school_name, date_text, food_dicts)

    await message.channel.send(embed=embed)

    return

async def food_image(client, message, month_offset):
    try:
        edu_code = await asyncio.wait_for(try_input_edu(client, message), timeout=10)
    except:
        cancel_message = await message.channel.send("10초가 지나 취소되었습니다.")
        await cancel_message.delete(delay=5)
        return

    try:
        school_info = await asyncio.wait_for(try_input_school(client, message, edu_code), timeout=30)
    except:
        cancel_message = await message.channel.send("30초가 지나 취소되었습니다.")
        await cancel_message.delete(delay=5)
        return
            
    school_code = school_info[0]
    school_name = school_info[1]

    start_date, end_date = functions.get_month_ends(month_offset)

    food_dicts = functions.get_food_info(edu_code, school_code, start_date, end_date)

    if food_dicts[0] == 0:
        await message.channel.send("급식 결과가 없습니다.")
        return

    available_type = []

    for food_dict in food_dicts[1]:
        if food_dict['food_name'] not in available_type:
            available_type.append(food_dict['food_name'])

    if len(available_type) > 1:
        try:
            food_type = await asyncio.wait_for(try_input_food_type(message, available_type), timeout=30)
        except:
            cancel_message = await message.channel.send("30초가 지나 취소되었습니다.")
            await cancel_message.delete(delay=5)
            return

        food_dicts[1] = [ food_dict for food_dict in food_dicts[1] if food_dict['food_name'] == food_type ]

    f = drawer.image_food_dict(school_name, food_dicts)

    image = discord.File(f)
    image.filename = "image.png"
    
    await message.channel.send(file=image)

    return