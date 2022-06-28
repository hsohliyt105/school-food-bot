# -*- coding: utf-8 -*-

import os
import asyncio

import discord
from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv(encoding="UTF-8")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
request_channel_list = [] #channel id

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@tasks.loop(seconds=1)
async def sex():
    print(1)

@tasks.loop(seconds=1)
async def sexy():
    print(2)

@client.event
async def on_connect():
    print("sex")
    sex.start()
    sexy.start()

@client.event
async def on_disconnect():
    print("sex?")
    sex.start()
    sexy.start()

client.run(DISCORD_TOKEN)