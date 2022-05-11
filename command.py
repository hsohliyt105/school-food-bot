# -*- coding: utf-8 -*-

import asyncio
import datetime

import discord

import helper
import functions
import drawer
import sql

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
    edu_code, school_code, school_name = await functions.get_user_info(client, message)

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
    edu_code, school_code, school_name = await functions.get_user_info(client, message)

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

async def register(client, message):
    try:
        edu_code = await asyncio.wait_for(functions.try_input_edu(client, message), timeout=helper.waiting_time)
    except TimeoutError:
        cancel_message = await message.channel.send(f"{helper.waiting_time}초가 지나 취소되었습니다.")
        await cancel_message.delete(delay=5)
        return

    try:
        school_info = await asyncio.wait_for(functions.try_input_school(client, message, edu_code), timeout=helper.waiting_time)
    except TimeoutError:
        cancel_message = await message.channel.send(f"{helper.waiting_time}초가 지나 취소되었습니다.")
        await cancel_message.delete(delay=5)
        return
            
    school_code = school_info[0]
    school_name = school_info[1]
      
    sql.save_user(message.author, edu_code, school_code, school_name)
    
    title = "등록에 성공했습니다!"
    desc = f"디스코드 id: {message.author.id}\n교육청 코드: {edu_code}\n학교 코드: {school_code}\n학교 이름: {school_name}"

    embed = discord.Embed(title=title, description=desc)

    await message.channel.send(embed=embed)

    return

async def delete(message):
    if sql.load_user(message.author.id) is None:
        await message.channel.send("삭제할 정보가 없어요. ")
        return

    confirm_message = await message.channel.send("정말로 자신의 학교 정보를 삭제하시겠습니까?: `!예` / `!아니오` (다시 등록할 수 있습니다.) ")
    recent_time = confirm_message.created_at
    passed_time = 0

    confirmed = False

    while not confirmed:
        messages = await message.channel.history(limit=4, after=recent_time).flatten()
        for mes in messages:
            if mes.content == ("!예"):
                confirmed = True
                
            if mes.content == ("!아니오"):
                await message.channel.send("취소되었습니다. ")
                return

        passed_time = datetime.datetime.utcnow() - recent_time
        if passed_time.total_seconds() > helper.waiting_time:
            await message.channel.send(f"{helper.waiting_time}초가 지나 취소되었습니다. ")
            return
        
        await asyncio.sleep(1)

    sql.delete_user(message.author.id)
    await message.channel.send("삭제되었습니다. ")

    return