# -*- coding: utf-8 -*-

from logging import raiseExceptions
import os
from datetime import datetime
import asyncio
import traceback

import discord
from discord.ext import tasks
from dotenv import load_dotenv

import command
import helper

abspath = os.path.abspath(__file__)
dir_name = os.path.dirname(abspath)
os.chdir(dir_name)

with open("general.log", "a") as general_log_f:
    general_log_f(f"{datetime.now()} Started.\n")

load_dotenv(dotenv_path=os.path.abspath(os.curdir+os.pardir), encoding="UTF-8")
DISCORD_TOKEN = os.getenv("TEST_TOKEN") # TEST_TOKEN or DISCORD_TOKEN
CLIENT_ID = os.getenv("TEST_ID") #TEST_ID or DISCORD_ID

intents = discord.Intents.default()
client = discord.Client(activity=discord.Game("!도움말"), intents=intents)

#상태 변경
@tasks.loop(seconds=(len(helper.command_list)+2)*helper.presence_time)
async def change_presence():
    for command in helper.command_list:
        client.activity = discord.Game(f"!{command}")
        await asyncio.sleep(helper.presence_time)
    client.activity = discord.Game(helper.version)
    await asyncio.sleep(helper.presence_time)
    client.activity = discord.Game(f"{len(client.guilds)}개의 서버에서 일")
    await asyncio.sleep(helper.presence_time)

#가동시의 반응
@client.event
async def on_ready():
    print(f"{client.user}이 디스코드에 접속했어요. ")

    for guild in client.guilds:
        print(guild.name)

    print(len(client.guilds))

    try:
        await change_presence.start()
        return
    except:
        return

#메시지를 받았을 때의 반응
@client.event
async def on_message(message):
    try:
        if message.author == client.user or message.author.bot:
            return
        
        if message.content.startswith("!"):
            if len(message.embeds) > 0:
                with open("general.log", "a") as general_log_f:
                    general_log_f.write(f"{datetime.now()} {message.guild} {message.channel} {message.author} title: {message.embeds[0].title} description: {message.embeds[0].description} fields: {message.embeds[0].fields} footer: {message.embeds[0].footer}\n")
            else: 
                with open("general.log", "a") as general_log_f:
                    general_log_f.writeprint(f"{datetime.now()} {message.guild} {message.channel} {message.author} {message.content}\n")

            string = message.content.split()

            if len(string[0]) > 1:
                string[0] = string[0][1:]
            else:
                return

            if string[0] == "도움말":
                await command.help_message(message)
                return

            if string[0] == "오늘급식":
                await command.food_message(client, message, 0, 0)
                return
            
            elif string[0] == "내일급식":
                await command.food_message(client, message, 1, 1)
                return

            elif string[0] == "이번주급식":
                await command.food_message(client, message, 0, 6)
                return

            elif string[0] == "다음주급식":
                await command.food_message(client, message, 7, 13)
                return

            elif string[0] == "이번달급식":
                await command.food_image(client, message, 0)
                return

            elif string[0] == "다음달급식":
                await command.food_image(client, message, 1)
                return

            elif string[0] == "등록":
                await command.register(client, message)
                return

            elif string[0] == "삭제":
                await command.delete(message)
                return

            elif string[0] == "구독":
                await command.subscribe(message)
                return

    except discord.errors.Forbidden:
        print(traceback.format_exc())
        with open("error.log", "a") as f:
            err_log = f"{datetime.now()} {message.guild} {message.channel} {message.author} {message.content}\n{traceback.format_exc()}\n"
            f.write(err_log)
            f.close()
        await message.channel.send(f"권한 에러가 발생했습니다! 이 링크(https://discord.com/oauth2/authorize?client_id={CLIENT_ID}&permissions=277025441856&scope=bot)를 통해 추방 후 다시 초대해주시길 바랍니다. *이 에러는 자동으로 제작자가 볼 수 있습니다.*")

    except:
        print(traceback.format_exc())
        with open("error.log", "a") as f:
            err_log = f"{datetime.now()} {message.guild} {message.channel} {message.author} {message.content}\n{traceback.format_exc()}\n"
            f.write(err_log)
            f.close()
        await message.channel.send("에러가 발생했습니다! *이 에러는 자동으로 제작자가 볼 수 있습니다.*")

    return

client.run(DISCORD_TOKEN)
