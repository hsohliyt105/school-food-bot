# -*- coding: utf-8 -*-

import os
import datetime
import math
import json

import requests
from dotenv import load_dotenv
import discord

import helper
import translator
import preferences

load_dotenv(encoding="UTF-8")
OSU_API_KEY = os.getenv("OSU_API_KEY")
EDU_API_KEY = os.getenv("EDU_API_KEY")

class Converter(object):
    def mods_string_to_int(string):
        mods = 0

        for i in range(0, len(string), 2):
            for name, member in helper.Mods.__members__.items():
                if string[i:i+2] == name:
                    mods = mods | member.value

        return mods

    def mods_int_to_string(mods):
        string = ""

        for name, member in helper.Mods.__members__.items():
            if mods & member.value != 0:
                string += name

        if string == "":
            string = "nm"

        return string

    def url_to_beatmap(url):
        beatmap = helper.Beatmap()

        string = url.split('/')

        if len(string) == 6:
            temp = string[4].split('#')

            beatmap.beatmapsetId = int(temp[0])
            beatmap.mode = Converter.mode_to_int(temp[1])
            beatmap.beatmapId = int(string[5])

            return beatmap

        elif len(string) == 5:
            if string[3] == "beatmaps":
                temp = string[4].split('?')

                beatmap.beatmapId = int(temp[0])
                beatmap.mode = Converter.mode_to_int(temp[1].split('=')[1])

                return beatmap

            if string[3] == "b":
                beatmap.beatmapId = int(string[4])

                return beatmap

        return

    def beatmap_to_url(beatmap, mode = -1):
        if mode == -1:
            return f"https://osu.ppy.sh/b/{beatmap.beatmapId}"
        return f"https://osu.ppy.sh/beatmapsets/{beatmap.beatmapsetId}#{helper.mode_en[mode]}/{beatmap.beatmapId}"

    def osu_user_to_url(user):
        return f"https://osu.ppy.sh/users/{user.userId}"

    def url_to_osu_user(url):
        user = helper.OsuUser()

        string = url.split('/')
        user_id = int(string[4])

        user.userId = user_id

        return user

    def second_to_string(second):
        string = ""

        if second >= 60:
            minute = int(second / 60)
            second = second % 60

            if minute >= 60:
                hour = int(minute / 60)
                minute = minute % 60

                if hour >= 24:
                    day = int(hour / 24)
                    hour = hour % 24

                    string += str(day) + "d "
                string += str(hour) + "h "
            string += str(minute) + "m "
        string += str(second) + "s "

        return string

    def second_to_time(second):
        string = ""
        minute = 0
        hour = 0

        if second >= 60:
            minute = int(second / 60)
            second = second % 60

            if minute >= 60:
                hour = int(minute / 60)
                minute = minute % 60

                if hour >= 24:
                    day = int(hour / 24)
                    hour = hour % 24
                string += str(hour) + ":"

            if minute < 10 and hour != 0:
                string += "0" + str(minute) + ":"
            else:
                string += str(minute) + ":"

        if second < 10 and (minute != 0 or hour != 0):
            string += "0" + str(second)
        else:
            string += str(second)

        return string

    def approved_to_string(approved):
        for name, member in helper.Approved.__members__.items():
            if member.value == approved:
                string = name

        return string

    def update_dict(dict, data):
        for key_dict, value_dict in data.items():
            for key_data, value_data in data.items():
                if key_dict == key_data:
                    dict[key_dict] = data[key_data]

        return dict

    def mode_to_int(string):
        for name, member in helper.Mode.__members__.items():
            if name == name:
                mode = member.value
                return mode

        return
    
    def find_username(string):
        try:
            first = string.index("'") + 1

            try: 
                second = string.index("'", first)

                username = string[first:second]
                return username

            except ValueError:
                return

        except ValueError:
            return

class HelpDiscord(object):
    def get_my_colour(client, channel):
        for member in channel.members:
            if client.user == member:
                colour = member.colour
                return colour

    def mention_to_id(mention):
        id = mention[3:-1]

        return id

class HelpOsu(object):
    def __init__(self, channel):
        self.channel = channel
        self._api = Api(channel)
        return

    def get_acc(self, mode, playdata):
        count300 = playdata.count300
        count100 = playdata.count100
        count50 = playdata.count50
        countmiss = playdata.countmiss
        countkatu = playdata.countkatu
        countgeki = playdata.countgeki

        total_hits = self.get_total_hits(mode, playdata)

        if mode == 0:
            acc = ((6 * count300 + 2 * count100 + count50) / (6 * total_hits))
        elif mode == 1:
            acc = ((2 * count300 + count100) / (2 * (total_hits)))
        elif mode == 2:
            acc = ((count300 + count100 + count50) / total_hits)
        else:
            acc = ((6 * (count300 + countgeki) + 4 * countkatu + 2 * count100 + count50) / (6 * (total_hits)))

        return acc

    def get_total_hits(self, mode, playdata):
        count300 = playdata.count300
        count100 = playdata.count100
        count50 = playdata.count50
        countmiss = playdata.countmiss
        countkatu = playdata.countkatu
        countgeki = playdata.countgeki

        if mode == 0:
            total = count300 + count100 + count50 + countmiss
        elif mode == 1:
            total = count300 + count100 + countmiss
        elif mode == 2:
            total = count300 + count100 + count50 + countmiss + countkatu
        else:
            total = countgeki + count300 + countkatu + count100 + count50 + countmiss

        return total

    # guess the number of misses + slider breaks from combo
    def get_effective_miss(self, playdata, beatmap):
        combo_based_miss = 0
        beatmap_max_combo = beatmap.maxCombo
        max_combo = playdata.maxCombo
        if beatmap.countSlider > 0:
            full_combo_threshold = beatmap_max_combo - 0.1 * beatmap.countSliders
            if max_combo < fullComboThreshold:
                combo_based_miss = full_combo_threshold / max(1, max_combo);

        # we're clamping misscount because since its derived from combo it can be higher than total hits and that breaks some calculations
        combo_based_miss = min(comboBasedMissCount, beatmap.totalHits)

        effective_miss = max(_numMiss, math.floor(comboBasedMissCount))

        return effective_miss

    def pp_calc(self, mode, playdata, acc = -1, beatmap = 0): #updated on 19.03.2021
        if acc == -1:
            acc = self.get_acc(mode, playdata)

        if beatmap == 0:
            beatmap = self._api.get_beatmaps(playdata.beatmapId)

        mods = playdata.enabledMods
        count_100 = playdata.count_100
        count_50 = playdata.count50
        count_miss = playdata.countmiss
        
        count_normal = beatmap.countNormal
        count_slider = beatmap.countSlider
        count_spinner = beatmap.countSpinner
        if mode != 3:
            if mode == 1:
                max_combo = count_normal
            else:
                max_combo = beatmap.maxCombo
            
            if playdata.maxCombo == 0:
                combo = max_combo
            else:
                combo = playdata.maxCombo
        if playdata.score == 0:
            score = 1000000
        else:
            score = playdata.score

        difficultyrating = beatmap.diffRating

        self.convert_map(beatmap, mode=mode, mods=mods)

        if mode == 0:
            count_effective_miss = get_effective_miss(playdata, beatmap)

            diff_aim = beatmap.diffAim
            diff_speed = beatmap.diffSpeed
    
            if mods & helper.Mods.td.value != 0:
                diff_aim = diff_aim ** 0.8

            aim_value = ((5 * max(1, diff_aim / 0.0675) - 4) ** 3) / 100000

            total_hits = count_normal + count_slider + count_spinner

            if total_hits > 2000:
                length_bonus = 1.35 + math.log10(total_hits / 2000 * 0.5)
            else:
                length_bonus = 0.95 + 0.4 * total_hits / 2000

            aim_value *= length_bonus

            if count_effective_miss > 0:
                aim_value *= 0.97 * (1 - (count_effective_miss / total_hits) ** 0.775) ** count_effective_miss

            if max_combo > 0:
                aim_value *= min((combo ** 0.8) / (max_combo ** 0.8), 1)

            approach_rate_factor = 0

            if beatmap.ar > 10.33:
                approach_rate_factor += 0.4 * (beatmap.ar - 10.33)
            elif beatmap.ar < 8:
                approach_rate_factor += 0.01 * (8 - beatmap.ar)

            aim_value *= 1 + approach_rate_factor * length_bonus

            if mods & helper.Mods.hd.value != 0:
                aim_value *= 1 + 0.04 * (12 - beatmap.ar)

            estimate_difficult_sliders = beatmap.countSlider * 0.15

            if (beatmap.NumSliders() > 0):
		        estimate_slider_ends_dropped = min(max(min(count_100 + count_50 + count_miss, max_combo - combo), 0), estimate_difficult_sliders)
		        slider_factor = beatmap.DifficultyAttribute(_mods, Beatmap::SliderFactor)
		        f32 sliderNerfFactor = (1.0f - sliderFactor) * std::pow(1.0f - estimateSliderEndsDropped / estimateDifficultSliders, 3) + sliderFactor
		        _aimValue *= sliderNerfFactor

            aim_value *= 0.5 + acc / 2
            aim_value *= 0.98 + (beatmap.od ** 2 / 2500)



            speed_value = ((5 * max(1, diff_speed / 0.0675) - 4) ** 3) / 100000

            if total_hits > 2000:
                length_bonus = 1.35 + math.log10(((total_hits) / 2000) * 0.5)
            else:
                length_bonus = 0.95 + 0.4 * total_hits / 2000

            speed_value *= length_bonus

            if count_miss > 0:
                speed_value += 0.97 * (1 - (count_miss / total_hits) ** 0.775) ** (count_miss ** 0.875)

            if max_combo > 0:
                speed_value *= min((combo ** 0.8) / (max_combo ** 0.8), 1)
            
            approach_rate_factor = 0
            if beatmap.ar > 10.33:
                approach_rate_factor += 0.4 * (beatmap.ar - 10.33) 

            speed_value *= 1 + min(approach_rate_factor, approach_rate_factor * total_hits / 1000)

            if mods & helper.Mods.hd.value != 0:
                speed_value *= 1 + 0.04 * (12 - beatmap.ar)

            speed_value *= (0.95 + beatmap.od ** 2 / 750) * acc ** ((14.5 - max(beatmap.od, 8)) / 2)
            if count_50 >= total_hits / 500:
                speed_value *= 0.98 ** (count_50 - total_hits / 500)
        


            if count_normal > 0:
                real_acc = max(0, total_hits * (acc - 1) / count_normal + 1)
            else:
                real_acc = 0

            acc_value = (1.52163 ** beatmap.od) * (real_acc ** 24) * 2.83

            acc_value *= min(1.15, (count_normal / 1000) ** 0.3)

            if mods & helper.Mods.hd.value != 0:
                acc_value *= 1.08

            if mods & helper.Mods.fl.value != 0:
                acc_value *= 1.02

        elif mode == 1:
            total_hits = count_normal + count_slider + count_spinner

            strain_value = ((5 * max(1, difficultyrating / 0.0075) - 4) ** 2) / 100000

            length_bonus = 1 + 0.1 * min(1, (total_hits / 1500))
            strain_value *= length_bonus

            strain_value *= 0.985 ** count_miss

            strain_value *= min(1, (combo ** 0.5) / (max_combo ** 0.5))

            strain_value *= acc

            if mods & helper.Mods.hd.value != 0:
                strain_value *= 1.025
            if mods & helper.Mods.fl.value != 0:
                strain_value *= 1.05 * length_bonus

            hit_window_300 = 50 - max(0, min(10, beatmap.od)) * 3

            acc_value = (150 / hit_window_300) ** 1.1
            acc_value *= (acc ** 15) * 22
            acc_value *= min(1.15, (total_hits / 1500) ** 0.3)

        elif mode == 2:
            total_hits = count_normal + count_slider
            value = ((5 * max(1, difficultyrating / 0.0049) - 4) ** 2) / 100000

            length_bonus = 0.95 + 0.3 * min(1, total_hits / 2500) + max(0, math.log10(total_hits / 2500) * 0.475)

            value *= length_bonus

            value *= 0.97 ** count_miss

            value *= (combo / max_combo) ** 0.8

            approach_rate_factor = 1

            if beatmap.ar > 9:
                approach_rate_factor += 0.1 * (beatmap.ar - 9)
            if beatmap.ar > 10:
                approach_rate_factor += 0.1 * (beatmap.ar - 10)
            elif beatmap.ar < 8:
                approach_rate_factor += 0.025 * (8 - beatmap.ar)

            value *= approach_rate_factor

            if mods & helper.Mods.hd.value != 0:
                if beatmap.ar <= 10:
                    value *= 1.05 + 0.075 * (10 - beatmap.ar)
                else:
                    value *= 1.01 + 0.04 * (11 - min(11, beatmap.ar))

            if mods & helper.Mods.fl.value != 0:
                value *= 1.35 * length_bonus

            value *= acc ** 5.5

        else:
            total_hits = count_normal + count_slider

            strain_value = ((5 * max(1, difficultyrating * 5) - 4) ** 2.2) / 135

            strain_value *= 1 + 0.1 * min(1, (total_hits / 1500))

            if score <= 500000:
                strain_value = 0
            elif score <= 600000:
                strain_value *= (score - 500000) / 100000 * 0.3
            elif score <= 700000:
                strain_value *= 0.3 + (score - 600000) / 100000 * 0.25
            elif score <= 800000:
                strain_value *= 0.55 + (score - 700000) / 100000 * 0.20
            elif score <= 900000:
                strain_value *= 0.75 + (score - 800000) / 100000 * 0.15
            else:
                strain_value *= 0.90 + (score - 900000) / 100000 * 0.1

            hit_window_300 = 65 - max(0, min(10, beatmap.od)) * 3

            acc_value = max(0, 0.2 - ((hit_window_300 - 34) * 0.006667)) * strain_value * ((max(0, (score - 960000)) / 40000) ** 1.1)
        
        if mode == 0:
            multiplier = 1.12
        elif mode == 1:
            multiplier = 1.1
            if mods & helper.Mods.hd.value != 0:
                multiplier *= 1.1
        elif mode == 2:
            multiplier = 1
        else:
            multiplier = 0.8

        if mods & helper.Mods.ez.value != 0 and mode == 3:
            multiplier *= 0.5
        if mods & helper.Mods.nf.value != 0:
            if mode == 0:
                multiplier *= max(0.9, 1 - 0.02 * count_miss);
            multiplier *= 0.9
        if mods & helper.Mods.so.value != 0:
            if mode == 0:
                multiplier *= 0.95
            else:
                multiplier *= 1 - (count_spinner / total_hits) ** 0.85


        if mode == 0:
            total_value = ((aim_value ** 1.1 + speed_value ** 1.1 + acc_value ** 1.1 + flashlight_value ** 1.1) ** (1 / 1.1)) * multiplier
        elif mode == 2:
            total_value = value * multiplier
        else:
            total_value = ((strain_value ** 1.1 + acc_value ** 1.1) ** (1 / 1.1)) * multiplier

        playdata.pp = total_value

        return total_value

    def mania_score_assume(self, score):
        return round((math.log(score) / math.log(1000000)) ** 2 * 1000000, 0)
    
    def load_osu(self, message, string):
        mode = 0
        osu_id = 0
        user = preferences.load_user(message.author.id)

        mode_found = False
        for temp in string:
            if Identifier.is_mode(temp):
                mode = Converter.mods_string_to_int(temp)
                mode_found = True
                break

        if not mode_found:
            if user is not None:
                mode = user['mode']

        user_found = False

        username = Converter.find_username(message.content)
        if username is not None:
            got_user = self._api.get_user(username=username, mode=mode)
            if got_user is not None:
                osu_id = got_user.userId

        else:
            for temp in string:
                if Identifier.is_int(temp):
                    osu_id = int(temp)
                    user_found = True
                    break
                elif Identifier.is_osu_user_url(temp):
                    osu_id = url_to_osu_user(temp).userId
                    user_found = True
                    break

            if not user_found:
                if user is not None:
                    if 'osu_id' in user.keys():
                        osu_id = user['osu_id']
                else:
                    return

        data = {
            'osu_id': osu_id,
            'mode': mode
        }

        return data

    def add_string_play(self, playdata, mode = 0, language = "en", beatmap = 0):
        f = open('translation/'+language+'.json')
        trans = json.load(f)['func_add_embed_play']
        f.close()
        f = open('translation/variables.json')
        trans_var = json.load(f)
        f.close()

        s_without_choke = trans['without_choke']
        s_max_pp = trans['max_pp']
        s_cleared = trans['cleared']

        if beatmap == 0:
            beatmap = self._api.get_beatmaps(playdata.beatmapId, mode=mode, mods=playdata.enabledMods)
        beatmap_url = Converter.beatmap_to_url(beatmap)

        if playdata.pp == -1:
            pp = self.pp_calc(mode, playdata, beatmap=beatmap)

        else:
            pp = playdata.pp

        acc = self.get_acc(mode, playdata)
        mods_str = Converter.mods_int_to_string(playdata.enabledMods)
        total_hits = beatmap.countNormal + beatmap.countSlider + beatmap.countSpinner
        hits_complete = self.get_total_hits(mode, playdata)
        hits_ratio = ""
        rank_emoji = ""
            
        if playdata.rank == "XH":
            rank_emoji = "<:ranking_XH:804020037085167647>"
        elif playdata.rank == "X":
            rank_emoji = "<:ranking_X:804020026726154261>"
        elif playdata.rank == "SH":
            rank_emoji = "<:ranking_SH:804019537484972072>"
        elif playdata.rank == "S":
            rank_emoji = "<:ranking_S:804019525107318834>"
        elif playdata.rank == "A":
            rank_emoji = "<:ranking_A:804019505537351724>"
        elif playdata.rank == "B":
            rank_emoji = "<:ranking_B:804019491615801354>"
        elif playdata.rank == "C":
            rank_emoji = "<:ranking_C:804019480338497568>"
        elif playdata.rank == "D":
            rank_emoji = "<:ranking_D:804019468840861766>"
        elif playdata.rank == "F":
            rank_emoji = "<:ranking_F:804026528400408616>"

        if mode == 0:
            hits_ratio = f"`{playdata.count300} / {playdata.count100} / {playdata.count50} / {playdata.countmiss}`"
        elif mode == 1:
            hits_ratio = f"`{playdata.count300} / {playdata.count100} / {playdata.countmiss}`"
        elif mode == 2:
            hits_ratio = f"`{playdata.count300} / {playdata.count100} / {playdata.count50} / {playdata.countmiss}`"
        else:
            hits_ratio = f"`{playdata.countgeki} / {playdata.count300} / {playdata.countkatu} / {playdata.count100} / {playdata.count50} / {playdata.countmiss}`"
            
        value = f"\n\n**[{beatmap.title} [{beatmap.version}]]({beatmap_url})** + `{mods_str.upper()}` - ★{round(beatmap.diffRating, 2)}"
        value += f"\n{rank_emoji} {round(100*acc, 2)}% • {playdata.maxCombo}x/{beatmap.maxCombo}x • {hits_ratio} • {playdata.score}\nPP: __**{round(pp ,2)}**__"

        if playdata.rank == "F":
            if mode == 3:
                if playdata.count100 + playdata.count50 + playdata.countmiss != 0:
                    cleared = helper.OsuPlayData(playdata)

                    cleared.countgeki += total_hits - hits_complete
                    cleared.score = min(1000000, cleared.score * total_hits / hits_complete)
                    cleared_acc = self.get_acc(mode, cleared)

                    cleared_pp = self.pp_calc(mode, cleared, acc=cleared_acc, beatmap=beatmap)

                    value += f' • {s_cleared}: **{round(cleared_pp, 2)}** ({round(cleared.score)}, {round(100*cleared_acc, 2)}%)'
                
            elif mode != 2:
                if playdata.maxCombo < beatmap.maxCombo:
                    cleared = helper.OsuPlayData(playdata)

                    cleared.count300 += total_hits - hits_complete
                    cleared.maxCombo = max(cleared.maxCombo, beatmap.maxCombo * (total_hits - hits_complete) / total_hits)
                    cleared_acc = self.get_acc(mode, cleared)

                    cleared_pp = self.pp_calc(mode, cleared, acc=cleared_acc, beatmap=beatmap)

                    value += f' • {s_cleared}: **{round(cleared_pp, 2)}** ({round(100*cleared_acc, 2)}%)'

        else:
            if mode == 3:
                if playdata.count100 + playdata.count50 + playdata.countmiss != 0:
                    non_choke = helper.OsuPlayData(playdata)

                    non_choke.countgeki += playdata.count100 + playdata.count50 + playdata.countmiss
                    non_choke.count100 = 0
                    non_choke.count50 = 0
                    non_choke.countmiss = 0
                    non_choke.score = self.mania_score_assume(non_choke.score)
                    non_choke_acc = self.get_acc(mode, non_choke)

                    non_choke_pp = self.pp_calc(mode, non_choke, acc=non_choke_acc, beatmap=beatmap)

                    value += f' • {s_without_choke}: **{round(non_choke_pp, 2)}** ({round(non_choke.score)})'
                
            elif mode != 2:
                if playdata.maxCombo < beatmap.maxCombo:
                    non_choke = helper.OsuPlayData(playdata)

                    non_choke.count300 += non_choke.countmiss
                    non_choke.countmiss = 0
                    non_choke.maxCombo = beatmap.maxCombo
                    non_choke_acc = self.get_acc(mode, non_choke)

                    non_choke_pp = self.pp_calc(mode, non_choke, acc=non_choke_acc, beatmap=beatmap)

                    value += f' • {s_without_choke}: **{round(non_choke_pp, 2)}** ({round(100*non_choke_acc, 2)}%)'

        if mode == 3:
            if playdata.score != 1000000:
                max_pp = helper.OsuPlayData(playdata)
                max_pp.score = 1000000
                max_pp_acc = 1

                max_pp_pp = self.pp_calc(mode, max_pp, acc=max_pp_acc, beatmap=beatmap)

                value += f' • {s_max_pp}: **{round(max_pp_pp, 2)}**'

        else:
            if acc != 1:
                max_pp = helper.OsuPlayData(playdata)
                max_pp.count300 = total_hits
                max_pp.count100 = 0
                max_pp.count50 = 0
                max_pp.countmiss = 0
                max_pp.maxCombo = beatmap.maxCombo
                max_pp_acc = 1

                max_pp_pp = self.pp_calc(mode, max_pp, acc=max_pp_acc, beatmap=beatmap)

                value += f' • {s_max_pp}: **{round(max_pp_pp, 2)}**'

        return value

    def convert_map(self, beatmap, mode = 0, mods = 0):
        if beatmap.converted == True:
            return

        if mods & helper.Mods.hr.value != 0:
            beatmap.cs = min(10, 1.3 * beatmap.cs)
            beatmap.od = min(10, 1.4 * beatmap.od)
            beatmap.ar = min(10, 1.4 * beatmap.ar)
            beatmap.hp = min(10, 1.4 * beatmap.hp)
        elif mods & helper.Mods.ez.value != 0:
            beatmap.cs = max(0, 0.5 * beatmap.cs)
            beatmap.od = max(0, 0.5 * beatmap.od)
            beatmap.ar = max(0, 0.5 * beatmap.ar)
            beatmap.hp = max(0, 0.5 * beatmap.hp)

        if mods & helper.Mods.dt.value != 0:
            time_mult = 1.5
        elif mods & helper.Mods.ht.value != 0:
            time_mult = 0.75
        else:
            time_mult = 1

        od0_ms = [79.5, 49.5, 0, 64.5]
        od_ms_step = [6, 3, 0, 3]

        if mods & (helper.Mods.dt.value | helper.Mods.ht.value) != 0:
            if mode != 2:
                beatmap.od = (od0_ms[mode] - (od0_ms[mode] - beatmap.od * od_ms_step[mode]) / time_mult) / od_ms_step[mode]
            if mode == 0 or mode == 2:
                if beatmap.ar < 5:
                    ar_ms = (1200 + (5 - beatmap.ar) * 120) / time_mult
                else:
                    ar_ms = (1200 + (5 - beatmap.ar) * 150) / time_mult
            
                if ar_ms > 1200:
                    beatmap.ar = (ar_ms - 1200) / 120
                else:
                    beatmap.ar = 5 + (1200 - ar_ms) / 150

        beatmap.bpm = beatmap.bpm * time_mult
        beatmap.totalLength = int(beatmap.totalLength / time_mult)
        beatmap.converted = True

        return

class Api(object):
    def __init__(self, channel):
        self.channel = channel
        return

    def get_beatmaps(self, beatmap_id, mode = 0, mods = 0):
        mods = mods & helper.diff_change_mods
        params = {
                    'k': OSU_API_KEY,
                    'b': beatmap_id,
                    'limit': 1,
                    'mode': mode,
                    'a': 1,
                    'mods': mods
                    }
        r = requests.get("https://osu.ppy.sh/api/get_beatmaps", params)

        if len(r.json()) == 0:
            return
    
        beatmap = helper.Beatmap(r.json()[0])

        preferences.save_channel(self.channel, recent_beatmap_id=beatmap_id)

        return beatmap

    def get_user(self, username = '', user_id = 0, mode = 0):
        params = {
                    'k': OSU_API_KEY,
                    'm': mode
                    }
        if username != '':
            params['type'] = "string"
            params['u'] = username
        elif user_id != 0:
            params['type'] = "id"
            params['u'] = user_id
        else:
            return

        r = requests.get("https://osu.ppy.sh/api/get_user", params)

        if len(r.json()) == 0:
            return

        if r.json()[0]['user_id'] == "3":
            return
    
        user = helper.OsuUser(r.json()[0])

        return user

    def get_user_best(self, username = "", user_id = 0, mode = 0, limit = 5):
        params = {
                    'k': OSU_API_KEY,
                    'm': mode,
                    'limit': limit
                    }
        if username != "":
            params['type'] = "string"
            params['u'] = username
        elif user_id != 0:
            params['type'] = "id"
            params['u'] = user_id
        else:
            return

        r = requests.get("https://osu.ppy.sh/api/get_user_best", params)

        if len(r.json()) == 0:
            return

        playdata = []

        for temp in r.json():
            playdata.append(helper.OsuPlayData(temp))
    
        return playdata

    def get_user_recent(self, username = "", user_id = 0, mode = 0):
        params = {
                    'k': OSU_API_KEY,
                    'm': mode,
                    'limit': 5
                    }
        if username != "":
            params['type'] = "string"
            params['u'] = username
        elif user_id != 0:
            params['type'] = "id"
            params['u'] = user_id
        else:
            return

        r = requests.get("https://osu.ppy.sh/api/get_user_recent", params)

        if len(r.json()) == 0:
            return

        result = []

        for temp in r.json():
            result.append(helper.OsuPlayData(temp))
    
        return result

    def get_scores(self, beatmap_id, username = "", user_id = 0, mode = 0):
        params = {
                    'k': OSU_API_KEY,
                    'b': beatmap_id,
                    'm': mode
                    }
        if username != "":
            params['type'] = "string"
            params['u'] = username
        elif user_id != 0:
            params['type'] = "id"
            params['u'] = user_id
        else:
            return

        r = requests.get("https://osu.ppy.sh/api/get_scores", params)

        if len(r.json()) == 0:
            return

        playdata = []

        for temp in r.json():
            temp['beatmap_id'] = beatmap_id
            playdata.append(helper.OsuPlayData(temp))
    
        return playdata

    def get_beatmap_cover_url(self, beatmapset_id):
        return f"https://assets.ppy.sh/beatmaps/{beatmapset_id}/covers/cover.jpg"

    def get_beatmap_thumb_url(self, beatmapset_id):
        return f"https://b.ppy.sh/thumb/{beatmapset_id}l.jpg"

    def get_user_image_url(self, user_id):
        return f"http://s.ppy.sh/a/{user_id}"

class Identifier(object):
    def is_int(string):
        try:
            temp = int(string)
            return True

        except ValueError:
            return False

    def is_mods(string):
        if len(string) > 64:
            return False

        for i in range(0, len(string), 2):
            if Converter.mods_string_to_int(string[i:i+2]) == 0:
                return False
                    
        return True

    def is_mode(string):
        if not (translator.alias.mode(string) is None):
            return True
        return False

    def is_beatmap_url(string):
        temp = string.split('/')
        if len(temp) == 6:
            if temp[2] == "osu.ppy.sh" and temp[3] == "beatmapsets":
                return True
        elif len(temp) == 5:
            if temp[2] == "osu.ppy.sh" and temp[3] == "b":
                return True
            elif temp[2] == "osu.ppy.sh" and temp[3] == "beatmaps":
                return True
        
        return False

    def is_osu_user_url(string):
        temp = string.split('/')
        if len(temp) == 5:
            if temp[2] == "osu.ppy.sh" and temp[3] == "users":
                return True

        return False

    def is_language(string):
        if not(translator.alias.language(string) is None):
            return True
        return False

    def is_mention(string):
        if string[:3] == "<@!" and string[-1:] == ">" and Identifier.is_int(string[3:-1]):
            return True
        return False