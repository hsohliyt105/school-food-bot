# -*- coding: utf-8 -*-

import os

import json
import pymysql
from dotenv import load_dotenv
import discord

import functions

load_dotenv(encoding="UTF-8")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")

def save_channel(channel, recent_beatmap_id = None):
    conn = pymysql.connect(host="localhost", user="root", db="osu_bot", password=MYSQL_PASSWORD,charset="utf8", cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()

    if recent_beatmap_id is None:
        recent_beatmap_id = "NULL"

    try:
        sql = f"INSERT INTO {str(channel.type)}_channel(id, recent_beatmap_id) VALUES({channel.id}, {recent_beatmap_id})"
        cur.execute(sql)
        conn.commit()

    except:
        if recent_beatmap_id != "NULL":
            sql = f"UPDATE {str(channel.type)}_channel SET recent_beatmap_id={recent_beatmap_id} WHERE id={channel.id}"
            cur.execute(sql)
            conn.commit()

    conn.close()

    return

def load_channel(channel, type="guild"):
    conn = pymysql.connect(host="localhost", user="root", db="osu_bot", password="Holyshit102!",charset="utf8", cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()

    sql = f"SELECT * FROM {str(channel.type)}_channel WHERE id={channel.id}"
    cur.execute(sql)
    result = cur.fetchall()

    if len(result) == 0:
        return

    return result[0]

def create_user(discord_id, language = "en", osu_id = 0, mode = 0):
    user = {
        'discord_id': discord_id,
        'language': language,
        'osu_id': osu_id,
        'mode': mode
    }
    return user

def save_user_osu(user, osu_id, mode):
    conn = pymysql.connect(host="localhost", user="root", db="osu_bot", password="Holyshit102!",charset="utf8", cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()

    try:
        sql = f"INSERT INTO user(discord_id, osu_id, mode) VALUES({user.id}, {osu_id}, {mode})"
        cur.execute(sql)
        conn.commit()

    except:
        sql = f"UPDATE user SET discord_id={user.id}, osu_id={osu_id}, mode={mode} WHERE discord_id={user.id}"
        cur.execute(sql)
        conn.commit()

    conn.close()

    return

def save_user_language(user, language):
    conn = pymysql.connect(host="localhost", user="root", db="osu_bot", password="Holyshit102!",charset="utf8", cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()

    try:
        sql = f"INSERT INTO user(discord_id, language) VALUES({user.id}, '{language}')"
        cur.execute(sql)
        conn.commit()

    except:
        sql = f"UPDATE user SET language='{language}' WHERE discord_id={user.id}"
        cur.execute(sql)
        conn.commit()

    conn.close()

    return

def load_user(discord_id):
    conn = pymysql.connect(host="localhost", user="root", db="osu_bot", password="Holyshit102!", charset="utf8", cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()

    sql = f"SELECT * FROM user WHERE discord_id={discord_id}"
    cur.execute(sql)
    result = cur.fetchall()

    if len(result) == 0:
        return

    return result[0]
