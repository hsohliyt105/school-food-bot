# -*- coding: utf-8 -*-

import os
from datetime import datetime

import discord
from dotenv import load_dotenv

import command

load_dotenv(encoding="UTF-8")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
request_channel_list = [] #channel id

intents = discord.Intents.default()
client = discord.Client(activity=discord.Game("!도움말"), intents=intents)

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

client.run(DISCORD_TOKEN)
