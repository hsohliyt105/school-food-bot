# -*- coding: utf-8 -*-

import os
from datetime import datetime
import json
import asyncio

import discord
from dotenv import load_dotenv

import functions
import helper

load_dotenv(encoding="UTF-8")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
request_channel_list = [] #channel id

intents = discord.Intents.default()
client = discord.Client(activity=discord.Game("!오늘급식 / !내일급식 / !이번주급식 / !다음주급식"), intents=intents)

#가동시의 반응
@client.event
async def on_ready():
    print(f"{client.user}이 디스코드에 접속했어요. ")

#메시지를 받았을 때의 반응
@client.event
async def on_message(message):
    print(f"{datetime.now()} {message.channel} {message.author} {message.content}")

    if message.author == client.user or message.author.bot:
        return
        
    if message.content.startswith("!"):
        string = message.content.split()

        if len(string[0]) > 1:
            string[0] = string[0][1:]
        else:
            return

        if string[0] == "오늘급식":
            try:
                edu_code = await asyncio.wait_for(functions.try_input_edu(client, message), timeout=10)
            except:
                cancel_message = await message.channel.send("10초가 지나 취소되었습니다.")
                await cancel_message.delete(delay=5)
                return

            try:
                school_info = await asyncio.wait_for(functions.try_input_school(client, message, edu_code), timeout=30)
            except:
                cancel_message = await message.channel.send("30초가 지나 취소되었습니다.")
                await cancel_message.delete(delay=5)
                return
            
            school_code = school_info[0]
            school_name = school_info[1]

            today_date = functions.get_korean_time(0)

            food_dicts = functions.get_food_info(edu_code, school_code, today_date, today_date)

            if food_dicts[0] == 0:
                await message.channel.send("결과가 없습니다.")
                return

            colour = functions.get_my_colour(client, message.channel)
            embed = functions.format_food_dict(colou, school_name, today_date, food_dicts)
            await message.channel.send(embed=embed)

            return
            
        elif string[0] == "내일급식":
            try:
                edu_code = await asyncio.wait_for(functions.try_input_edu(client, message), timeout=10)
            except:
                cancel_message = await message.channel.send("10초가 지나 취소되었습니다.")
                await cancel_message.delete(delay=5)
                return

            try:
                school_info = await asyncio.wait_for(functions.try_input_school(client, message, edu_code), timeout=30)
            except:
                cancel_message = await message.channel.send("30초가 지나 취소되었습니다.")
                await cancel_message.delete(delay=5)
                return
            
            school_code = school_info[0]
            school_name = school_info[1]

            tomarrow_date = functions.get_korean_time(1)

            food_dicts = functions.get_food_info(edu_code, school_code, tomarrow_date, tomarrow_date)

            if food_dicts[0] == 0:
                await message.channel.send("결과가 없습니다.")
                return

            colour = functions.get_my_colour(client, message.channel)
            embed = functions.format_food_dict(colour, school_name, tomarrow_date, food_dicts)
            await message.channel.send(embed=embed)

            return

        elif string[0] == "이번주급식":
            try:
                edu_code = await asyncio.wait_for(functions.try_input_edu(client, message), timeout=10)
            except:
                cancel_message = await message.channel.send("10초가 지나 취소되었습니다.")
                await cancel_message.delete(delay=5)
                return

            try:
                school_info = await asyncio.wait_for(functions.try_input_school(client, message, edu_code), timeout=30)
            except:
                cancel_message = await message.channel.send("30초가 지나 취소되었습니다.")
                await cancel_message.delete(delay=5)
                return
            
            school_code = school_info[0]
            school_name = school_info[1]

            offset = functions.to_monday_offset()
            mon_date = functions.get_korean_time(-offset)
            sun_date = functions.get_korean_time(-offset + 6)

            food_dicts = functions.get_food_info(edu_code, school_code, mon_date, sun_date)

            if food_dicts[0] == 0:
                await message.channel.send("결과가 없습니다.")
                return

            colour = functions.get_my_colour(client, message.channel)
            date_text = f"{mon_date}-{sun_date}"
            embed = functions.format_food_dict(colour, school_name, tomarrow_date, food_dicts)
            await message.channel.send(embed=embed)

            return

        elif string[0] == "다음주급식":
            
            try:
                edu_code = await asyncio.wait_for(functions.try_input_edu(client, message), timeout=10)
            except:
                cancel_message = await message.channel.send("10초가 지나 취소되었습니다.")
                await cancel_message.delete(delay=5)
                return

            try:
                school_info = await asyncio.wait_for(functions.try_input_school(client, message, edu_code), timeout=30)
            except:
                cancel_message = await message.channel.send("30초가 지나 취소되었습니다.")
                await cancel_message.delete(delay=5)
                return
            
            school_code = school_info[0]
            school_name = school_info[1]

            offset = functions.to_monday_offset()
            mon_date = functions.get_korean_time(-offset + 7)
            sun_date = functions.get_korean_time(-offset + 13)

            food_dicts = functions.get_food_info(edu_code, school_code, mon_date, sun_date)

            if food_dicts[0] == 0:
                await message.channel.send("결과가 없습니다.")
                return

            colour = functions.get_my_colour(client, message.channel)
            date_text = f"{mon_date}-{sun_date}"
            embed = functions.format_food_dict(colour, school_name, tomarrow_date, food_dicts)
            await message.channel.send(embed=embed)

            return

client.run(DISCORD_TOKEN)