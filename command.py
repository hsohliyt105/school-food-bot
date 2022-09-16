# -*- coding: utf-8 -*-

from asyncio import CancelledError, TimeoutError, sleep, wait_for
from datetime import datetime

from discord import File, Embed

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
        
        await sleep(1)

async def help_message(message):
    command_list_text = f"`{'`, `'.join(helper.command_list)}`"

    embed = Embed(title="명령어 목록", description=command_list_text)

    await message.channel.send(embed=embed)

    return

async def food_message(client, message, start_offset, end_offset):
    user_info = await functions.get_user_info(client, message)
    if user_info is None:
        return
    edu_code, school_code, school_name = user_info

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
    user_info = await functions.get_user_info(client, message)
    if user_info is None:
        return
    edu_code, school_code, school_name = user_info

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
            food_type = await wait_for(try_input_food_type(message, available_type), timeout=30)
        except:
            cancel_message = await message.channel.send("30초가 지나 취소되었습니다.")
            await cancel_message.delete(delay=5)
            return

        food_dicts[1] = [ food_dict for food_dict in food_dicts[1] if food_dict['food_name'] == food_type ]

    f = drawer.image_food_dict(school_name, food_dicts)

    image = File(f)
    image.filename = "image.png"
    
    await message.channel.send(file=image)

    return

async def register(client, message):
    try:
        edu_code = await wait_for(functions.try_input_edu(client, message), timeout=helper.waiting_time)
    except TimeoutError:
        cancel_message = await message.channel.send(f"{helper.waiting_time}초가 지나 취소되었습니다.")
        await cancel_message.delete(delay=5)
        return

    try:
        school_info = await wait_for(functions.try_input_school(client, message, edu_code), timeout=helper.waiting_time)
    except TimeoutError:
        cancel_message = await message.channel.send(f"{helper.waiting_time}초가 지나 취소되었습니다.")
        await cancel_message.delete(delay=5)
        return
            
    school_code = school_info[0]
    school_name = school_info[1]
      
    sql.save_user(message.author, edu_code, school_code, school_name)
    
    title = "등록에 성공했습니다!"
    desc = f"디스코드 id: {message.author.id}\n교육청 코드: {edu_code}\n학교 코드: {school_code}\n학교 이름: {school_name}"

    embed = Embed(title=title, description=desc)

    await message.channel.send(embed=embed)

    return

async def delete(message):
    if sql.load_user(message.author.id) is None:
        await message.channel.send("삭제할 정보가 없어요. ")
        return

    confirm_message = await message.channel.send("정말로 자신의 학교 정보를 삭제하시겠습니까?: `!예` / `!아니오` (다시 등록할 수 있습니다.) ")
    start_time = confirm_message.created_at
    await confirm_message.delete(delay=helper.waiting_time)

    try:
        confirmed = await wait_for(functions.try_confirm(message, start_time), helper.waiting_time)
    except TimeoutError and CancelledError:
            cancel_message = await message.channel.send(f"{helper.waiting_time}초가 지나 취소되었습니다. ")
            await cancel_message.delete(delay=5)
            return

    if confirmed:
        sql.delete_user(message.author.id)
        await message.channel.send("삭제되었습니다. ")

    else:
        await message.channel.send("취소되었습니다. ")

    return

async def subscribe(message):
    if sql.load_user(message.author) is not None:
        try:
            hour, minute = await wait_for(functions.try_input_time(), helper.waiting_time)

        except TimeoutError and CancelledError:
            cancel_message = await message.channel.send(f"{helper.waiting_time}초가 지나 취소되었습니다. ")
            await cancel_message.delete(delay=5)
            return

        sql.save_subscription(message.author, hour, minute)

        title = "구독에 성공했습니다!"
        desc = f"정보를 받을 시간: {hour}시 {minute}분"
        embed = Embed(title=title, description=desc)

        await message.channel.send(embed=embed)

        return
        
    else:
        await message.channel.send("등록된 정보가 없습니다. `!등록`을 먼저 사용하여 학교 정보를 등록해주세요.")

    return