# -*- coding: utf-8 -*-

import datetime
from enum import Enum

import functions

class Mods(Enum):
    nm = 0
    nf = 1
    ez = 2
    td = 4
    hd = 8
    hr = 16
    sd = 32
    dt = 64
    rx = 128
    ht = 256
    nc = 512 # Only set along with DoubleTime. i.e: NC only gives 576
    fl = 1024
    ap = 2048 # Autopilot
    so = 4096
    pf = 16384 # Only set along with SuddenDeath. i.e: PF only gives 16416  
    k4 = 32768
    k5 = 65536
    k6 = 131072
    k7 = 262144
    k8 = 524288
    fi = 1048576
    rd = 2097152
    cn = 4194304
    tg = 8388608
    k9 = 16777216
    kc = 33554432
    k1 = 67108864
    k3 = 134217728
    k2 = 268435456
    v2 = 536870912
    mr = 1073741824

class Beatmap(object):
    def __init__(self, data=-1):
        if data == -1:
            self.clear()
            return

        self.converted = False
        self.beatmapsetId = int(data['beatmapset_id'])
        self.beatmapId = int(data['beatmap_id'])
        self.approved = functions.Converter.approved_to_string(int(data['approved']))
        self.totalLength = int(data['total_length'])
        self.version = data['version']
        self.cs = float(data['diff_size'])
        self.od = float(data['diff_overall'])
        self.ar = float(data['diff_approach'])
        self.hp = float(data['diff_drain'])
        self.mode = int(data['mode'])
        self.countNormal = int(data['count_normal'])
        self.countSlider = int(data['count_slider'])
        self.countSpinner = int(data['count_spinner'])

        if data['artist_unicode'] is None:
            self.artist = data['artist']
        else:
            self.artist = data['artist_unicode']
    
        if data['title_unicode'] is None:
            self.title = data['title']
        else:
            self.title = data['title']

        self.creator = data['creator']
        self.creatorId = int(data['creator_id'])
        self.bpm = float(data['bpm'])
        self.favouriteCount = int(data['favourite_count'])
        self.rating = float(data['rating'])

        if int(data['video']) == 0:
            self.video = False
        else:
            self.video = True

        if int(data['download_unavailable']) == 0:
            self.downloadUnavailable = False
        else:
            self.downloadUnavailable = True

        self.playcount = int(data['playcount'])
        self.passcount = int(data['passcount'])

        if -2 <= int(data['approved']) <= 0:
            self.passrate = 0

        else:
            self.passrate = round(100 * self.passcount / self.playcount, 2)

        if data['max_combo'] is None:
            self.maxCombo = 0
        else:
            self.maxCombo = int(data['max_combo'])

        if data['diff_aim'] is None:
            self.diffAim = 0
        else:
            self.diffAim = float(data['diff_aim'])
        if data['diff_speed'] is None:
            self.diffSpeed = 0
        else:
            self.diffSpeed = float(data['diff_speed'])

        self.diffRating = float(data['difficultyrating'])
        return

    def clear(self):
        self.converted = False
        self.beatmapsetId = 0
        self.beatmapId = 0
        self.approved = ""
        self.totalLength = 0
        self.version = ""
        self.cs = 0.0
        self.od = 0.0
        self.ar = 0.0
        self.hp = 0.0
        self.mode = 0
        self.countNormal = 0
        self.countSlider = 0
        self.countSpinner = 0
        self.artist = ""
        self.artist = ""
        self.creator = ""
        self.creatorId = 0
        self.bpm = 0.0
        self.favouriteCount = 0
        self.rating = 0
        self.video = False
        self.downloadUnavailable = False
        self.playcount = 0
        self.passcount = 0
        self.passrate = 0
        self.maxCombo = 0
        self.diffAim = 0.0
        self.diffSpeed = 0.0
        self.diffRating = 0.0

class OsuPlayData(object):
    def __init__(self, data = -1):
        if data == -1:
            self.clear()
            return

        if type(data) is OsuPlayData:
            self.beatmapId = data.beatmapId
            self.score = data.score
            self.count300 = data.count300
            self.count100 = data.count100
            self.count50 = data.count50
            self.countmiss = data.countmiss
            self.maxCombo = data.maxCombo
            self.countkatu = data.countkatu
            self.countgeki = data.countgeki
            self.enabledMods = data.enabledMods
            self.userId = data.userId
            self.date = data.date
            self.rank = data.rank
            self.pp = data.pp

            return

        self.beatmapId = int(data['beatmap_id'])
        self.score = int(data['score'])
        self.count300 = int(data['count300'])
        self.count100 = int(data['count100'])
        self.count50 = int(data['count50'])
        self.countmiss = int(data['countmiss'])
        self.maxCombo = int(data['maxcombo'])
        self.countkatu = int(data['countkatu'])
        self.countgeki = int(data['countgeki'])
        self.enabledMods = int(data['enabled_mods'])
        self.userId = int(data['user_id'])
        self.date = datetime.datetime.strptime(data['date'], "%Y-%m-%d %X")
        self.rank = data['rank']

        if "pp" in data.keys():
            self.pp = float(data['pp'])
        else:
            self.pp = -1

        return

    def clear(self):
        self.beatmapId = 0
        self.score = 0
        self.username = ""
        self.count300 = 0
        self.count100 = 0
        self.count50 = 0
        self.countmiss = 0
        self.maxCombo = 0
        self.countkatu = 0
        self.countgeki = 0
        self.enabledMods = 0
        self.userId = 0
        self.date = datetime.datetime.now()
        self.rank = ""
        self.pp = -1

class OsuUser(object):
    def __init__(self, data = -1):
        if data == -1:
            self.clear()
            return

        self.userId = int(data['user_id'])
        self.username = data['username']
        self.playcount = int(data['playcount'])
        self.ppRank = int(data['pp_rank'])
        self.level = float(data['level'])
        self.ppRaw = float(data['pp_raw'])
        self.accuracy = float(data['accuracy'])
        self.country = data['country']
        self.totalTimePlayed = functions.Converter.second_to_time(int(data['total_seconds_played']))
        self.ppCountryRank = int(data['pp_country_rank'])

    def clear(self):
        self.userId = 0
        self.username = ""
        self.playcount = 0
        self.ppRank = 0
        self.level = 0.0
        self.ppRaw = 0.0
        self.accuracy = 0.0
        self.country = ""
        self.totalTimePlayed = ""
        self.ppCountryRank = 0
        
class Mode(Enum):
    osu = 0
    taiko = 1
    catch = 2
    mania = 3

class Approved(Enum):
    loved = 4
    qualified = 3
    approved = 2
    ranked = 1
    pending = 0
    WIP = -1
    graveyard = -2

mode_en = ["osu", "taiko", "catch", "mania"]

diff_change_mods = Mods.hr.value | Mods.dt.value | Mods.ez.value | Mods.ht.value 

