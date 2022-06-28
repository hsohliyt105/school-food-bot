# -*- coding: utf-8 -*-

import os

import pymysql
from dotenv import load_dotenv

load_dotenv(encoding="UTF-8")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")

def save_user(user, edu_code, school_code, school_name):
    conn = pymysql.connect(host="localhost", user="root", db="school_food_bot", password=MYSQL_PASSWORD, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()

    try:
        sql = f"INSERT INTO users(discord_id, edu_code, school_code, school_name) VALUES({user.id}, '{edu_code}', '{school_code}', '{school_name}')"
        cur.execute(sql)
        conn.commit()

    except:
        sql = f"UPDATE users SET edu_code='{edu_code}', school_code='{school_code}', school_name='{school_name}' WHERE discord_id={user.id}"
        cur.execute(sql)
        conn.commit()

    conn.close()

    return

def save_subscription(user, subscribe_hour, subscribe_min):
    conn = pymysql.connect(host="localhost", user="root", db="school_food_bot", password=MYSQL_PASSWORD, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()

    sql = f"UPDATE users SET subscribe_hour='{subscribe_hour}' subscribe_min='{subscribe_min}' WHERE discord_id={user.id}"
    cur.execute(sql)
    conn.commit()
    return 

def load_user(discord_id):
    conn = pymysql.connect(host="localhost", user="root", db="school_food_bot", password=MYSQL_PASSWORD, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()

    sql = f"SELECT * FROM users WHERE discord_id={discord_id}"
    cur.execute(sql) 
    result = cur.fetchall()
    conn.close()

    if len(result) == 0:
        return

    return result[0]

def delete_user(discord_id):
    conn = pymysql.connect(host="localhost", user="root", db="school_food_bot", password=MYSQL_PASSWORD, charset="utf8", cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()

    sql = f"DELETE FROM users WHERE discord_id={discord_id}"
    print(sql)
    cur.execute(sql) 
    
    conn.commit()
    conn.close()

    return