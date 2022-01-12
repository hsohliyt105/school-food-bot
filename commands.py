# -*- coding: utf-8 -*-

import os
import datetime
import shutil
import math
from enum import Enum
import pathlib
import time
import random
import json

import discord

import functions
import helper
import translator
import preferences

class commands(object):
    def __init__(self, client, message, user):
        self.client = client
        self.message = message
        self.user = user
        self._api = functions.Api(message.channel)
        self._helpOsu = functions.HelpOsu(message.channel)

    async def help(self, string):
        f = open('translation/'+self.user['language']+'.json')
        trans = json.load(f)['help']
        f.close()
        f = open('translation/commands.json')
        command_dict = json.load(f)
        f.close()
        
        s_title = trans['title']
        s_legend = trans['legend']
        s_add_help = trans['add_help']
        s_command = trans['command']
        s_usage = trans['usage']
        s_example = trans['example']
        s_description = trans['description']

        command_list = "`"
        for i in command_dict.values():
            command_list += i[self.user['language']] + "` • `"
        command_list = command_list[:-4]

        if len(string) == 1:
            title = s_title
            description = command_list + "\n\n" + s_add_help
            colour = functions.HelpDiscord.get_my_colour(self.client, self.message.channel)

            embed = discord.Embed(title=title, description=description, colour=colour)

            await self.message.channel.send(embed=embed)

            return

        if len(string) >= 2:
            help_com = translator.alias.command(string[1])

            if help_com is None:
                await self.wrong([s_command])
                return

            else:
                title = command_dict[help_com][self.user['language']]
                description = s_legend
                colour = functions.HelpDiscord.get_my_colour(self.client, self.message.channel)
                
                embed = discord.Embed(title=title, description=description, colour=colour)
                embed.add_field(name=s_usage, value=command_dict[help_com]['usage'][self.user['language']], inline=False)
                embed.add_field(name=s_example, value=command_dict[help_com]['example'][self.user['language']], inline=False)
                embed.add_field(name=s_description, value=command_dict[help_com]['description'][self.user['language']], inline=False)

                await self.message.channel.send(embed=embed)

                return
        return

    async def beatmap(self, string):
        mods = 0
        beatmap_id = 0
        mode = 0

        for temp in string:
            if functions.Identifier.is_mods(temp):
                mods = functions.Converter.mods_string_to_int(temp)
            elif functions.Identifier.is_int(temp):
                beatmap_id = int(temp)
            elif functions.Identifier.is_beatmap_url(temp):
                beatmap_id = functions.Converter.url_to_beatmap(temp).beatmapId
            elif functions.Identifier.is_mode(temp):
                mode = translator.alias.mode(temp)

        if beatmap_id == 0:
            channel = preferences.load_channel(self.message.channel)
            if channel is None:
                await self.missing(["beatmap id"])
                return
            beatmap_id = channel['recent_beatmap_id']

        beatmap = self._api.get_beatmaps(beatmap_id, mode=mode, mods=mods)

        f = open('translation/'+self.user['language']+'.json')
        trans = json.load(f)['beatmap']
        f.close()

        s_no_map_found = trans['no_map_found']
        s_main_page = trans['main_page']
        s_download = trans['download']
        s_no_vid_download = trans['no_vid_download']
        s_difficulty = trans['difficulty']
        s_aim = trans['aim']
        s_speed = trans['speed']
        s_creator = trans['creator']
        s_max_combo = trans['max_combo']
        s_passed = trans['passed']
        s_beatmap_id = trans['beatmap_id']
        s_estimated_pp = trans['estimated_pp']

        if beatmap is None:
            beatmap = self._api.get_beatmaps(beatmap_id, mods=mods)
            if beatmap is None:
                await self.message.channel.send(s_no_map_found)
                return

        map_url = functions.Converter.beatmap_to_url(beatmap, beatmap.mode)
        download_url = f"https://osu.ppy.sh/d/{beatmap.beatmapsetId}"
        no_vid_download_url = download_url + "n"
        thumb_url = self._api.get_beatmap_thumb_url(beatmap.beatmapsetId)

        creator = helper.OsuUser()
        creator.userId = beatmap.creatorId

        creator_url = functions.Converter.osu_user_to_url(creator)

        playdata = helper.OsuPlayData()
        playdata.beatmapId = beatmap.beatmapId
        playdata.enabledMods = mods

        playdata.score = 700000
        pp_95 = round(self._helpOsu.pp_calc(beatmap.mode, playdata, acc=0.95, beatmap=beatmap), 2)
        playdata.score = 800000
        pp_97 = round(self._helpOsu.pp_calc(beatmap.mode, playdata, acc=0.97, beatmap=beatmap), 2)
        playdata.score = 900000
        pp_99 = round(self._helpOsu.pp_calc(beatmap.mode, playdata, acc=0.99, beatmap=beatmap), 2)
        playdata.score = 1000000
        pp_100 = round(self._helpOsu.pp_calc(beatmap.mode, playdata, acc=1, beatmap=beatmap), 2)

        self._helpOsu.convert_map(beatmap, mode=beatmap.mode, mods=mods)

        title = f"{beatmap.title} [{beatmap.version}]  -  {beatmap.artist}"
        colour = functions.HelpDiscord.get_my_colour(self.client, self.message.channel)

        description = f"[{s_main_page}]({map_url}) • [{s_download}]({download_url})"
        if beatmap.video == True:
            description += f" • [{s_no_vid_download}]({no_vid_download_url})"

        difficulty = f"**{s_difficulty}**: ★{round(beatmap.diffRating, 2)}"
        if beatmap.mode == 0:
            difficulty += f" (**{s_aim}**: ★{round(beatmap.diffAim, 2)}, **{s_speed}**: ★{round(beatmap.diffSpeed, 2)})"

        total_objects = f"<:total_length:802878638344110091>{functions.Converter.second_to_time(beatmap.totalLength)} •  <:bpm:802878560380649472>{beatmap.bpm} • <:count_circles:802878577908908032>{beatmap.countNormal} • <:count_sliders:802878591607111730>{beatmap.countSlider}"
        
        if beatmap.mode != 3:
             total_objects += f" • <:count_spinners:802878611123208242>{beatmap.countSpinner}"

        if beatmap.mode == 0:
            ruleset = f"**CS**: {round(beatmap.cs, 2)} • **AR**: {round(beatmap.ar, 2)} • **OD**: {round(beatmap.od, 2)} • **HP**: {round(beatmap.hp, 2)}"
        elif beatmap.mode == 2:
            ruleset = f"**CS**: {round(beatmap.cs, 2)} • **AR**: {round(beatmap.ar, 2)} • **HP**: {round(beatmap.hp, 2)}"
        else:
            ruleset = f"**OD**: {round(beatmap.od, 2)} • **HP**: {round(beatmap.hp, 2)}"

        description += f"\n\n**{s_creator}**: [{beatmap.creator}]({creator_url})\n{difficulty}\n{ruleset}"
        if beatmap.mode != 3:
            description += f"\n**{s_max_combo}**: {beatmap.maxCombo}"
        description += f"\n{total_objects}"
        if beatmap.mode != 3:
            pp = f"**95%**: {pp_95} **97%**: {pp_97} **99%**: {pp_99} **100%**: {pp_100}"
        else:
            pp = f"**700k**: {pp_95} **800k**: {pp_97} **900k**: {pp_99} **1M**: {pp_100}"

        footer = f"{beatmap.approved.capitalize()} • ❤ {beatmap.favouriteCount} • {beatmap.passrate}% {s_passed} • {s_beatmap_id}: {beatmap.beatmapId}"
        
        embed = discord.Embed(title=title, description=description, colour=colour)
        embed.add_field(name=s_estimated_pp, value=pp, inline=False)
        embed.set_thumbnail(url=thumb_url)
        embed.set_footer(text=footer)

        await self.message.channel.send(embed=embed)
        return

    async def set(self, string):
        if self.user['language'] is None:
            self.user['language'] = "en"

        f = open('translation/'+self.user['language']+'.json')
        trans = json.load(f)['set']
        f.close()
        f = open('translation/variables.json')
        trans_var = json.load(f)
        f.close()
        f = open('translation/general.json')
        temp = json.load(f)
        properties = temp['property']
        languages = temp['language']
        f.close()

        available_property = ""

        s_property = trans['property']


        for key, value in properties.items():
            available_property += ", ".join(value)
            available_property += ", "

        available_property = available_property[:-2]

        if len(string) < 2:
            await self.missing([f"{s_property} ({available_property})"])
            return

        property = translator.alias.property(string[1])

        if property == "language":
            s_language = trans['language']

            available_language = ""

            for key, value in languages.items():
                available_language += ", ".join(value)
                available_language += ", "

            available_language = available_language[:-2]

            if len(string) < 3:
                await self.missing([f'{s_language} ({available_language})'])
                return

            discord_id = self.message.author.id
            language = ""

            for temp in string:
                if functions.Identifier.is_language(temp):
                    language = translator.alias.language(temp)
                    break

            if language == "":
                await self.wrong([f'{s_language} ({available_language})'])
                return

            f = open('translation/'+language+'.json')
            trans = json.load(f)['set']
            f.close()

            s_language = trans['language']
            s_user_language = trans_var['language'][language][language]

            self.user['language'] = language

            preferences.save_user_language(self.message.author, language)
            data = {s_language: s_user_language}

            s_set_complete = trans['set_complete']

            title = f"{self.message.author} {s_set_complete}"

            result = ""
            for key, value in data.items():
                result += f"**{key}**: {value}\n"

            colour = functions.HelpDiscord.get_my_colour(self.client, self.message.channel)

            embed = discord.Embed(title=title, description=result, colour=colour)

            await self.message.channel.send(embed=embed)

            return

        elif property == "osu":
            s_osu_id = trans['osu_id']
            s_osu_user_url = trans['osu_user_url']
            s_or = trans['or']
            s_mode = trans['mode']
            s_user_not_found = trans['user_not_found']
            s_username = trans['username']

            if len(string) < 3:
                await self.missing([s_mode, f"{s_osu_id} {s_or} {s_osu_user_url} {s_or} '{s_username}'"])
                return

            if len(string) < 4:
                if functions.Identifier.is_int(string[2]) or functions.Identifier.is_osu_user_url(string[2]) or (not functions.Converter.find_username(self.message.content) is None):
                    await self.missing([s_mode])
                    return
                elif functions.Identifier.is_mode(string[2]):
                    await self.missing([f"{s_osu_id} {s_or} {s_osu_user_url} {s_or} '{s_username}'"])
                    return
                else:
                    await self.missing([s_mode, f'{s_osu_id} {s_or} {s_osu_user_url}'])
                    return

            user_found = False
            mode_found = False
            osu_id = 0
            mode = 0
            username = ""

            username = functions.Converter.find_username(self.message.content)
            if username is not None:
                user_found = True

            for i in range(2, len(string)):
                if functions.Identifier.is_int(string[i]):
                    user_found = True
                    osu_id = int(string[i])

                elif functions.Identifier.is_osu_user_url(string[i]):
                    user_found = True
                    osu_id = functions.Converter.url_to_osu_user(string[i]).userId

                elif functions.Identifier.is_mode(string[i]):
                    mode_found = True
                    mode = translator.alias.mode(string[i])


            if mode_found == False:
                await self.missing([s_mode])
                return
            if user_found == False:
                await self.missing([f"{s_osu_id} {s_or} {s_osu_user_url} {s_or} '{s_username}'"])
                return

            if username is None:
                user = self._api.get_user(user_id=osu_id, mode=mode)
            else:
                user = self._api.get_user(username=username, mode=mode)

            if user is None:
                await self.message.channel.send(f"{s_user_not_found}.")
                return

            osu_id = user.userId

            preferences.save_user_osu(self.message.author, osu_id, mode)

            username = user.username
            s_user_mode = trans_var['mode'][str(mode)][self.user['language']]

            data = {s_osu_id: osu_id, s_username: username, s_mode: s_user_mode}

            s_set_complete = trans['set_complete']

            title = f"{self.message.author} {s_set_complete}"

            result = ""
            for key, value in data.items():
                result += f"**{key}**: {value}\n"

            colour = functions.HelpDiscord.get_my_colour(self.client, self.message.channel)
            
            osu_profile_url = self._api.get_user_image_url(osu_id)

            embed = discord.Embed(title=title, description=result, colour=colour)
            embed.set_thumbnail(url=osu_profile_url)

            await self.message.channel.send(embed=embed)
            return

        else:
            await self.wrong([s_property])
            return

    async def recent(self, string):
        f = open('translation/'+self.user['language']+'.json')
        trans = json.load(f)['recent']
        f.close()
        f = open('translation/variables.json')
        trans_var = json.load(f)
        f.close()
        
        s_mode = trans['mode']
        s_osu_id = trans['osu_id']
        s_or = trans['or']
        s_username = trans['username']
        s_osu_user_url = trans['osu_user_url']
        s_osu_user_not_set = trans['osu_user_not_set']
        s_of_recent = trans['of_recent'] 
        s_no_recent_play = trans['no_recent_play']
        s_user_not_found = trans['user_not_found']
        s_completed = trans['completed']

        mode = 0
        osu_id = ""
        mode_found = False

        if functions.Converter.find_username(self.message.content) is not None:
            current_user = self._api.get_user(username=functions.Converter.find_username(self.message.content))

            if current_user is None:
                await self.message.channel.send(s_user_not_found)
                return

            osu_id = current_user.userId

        for i in range(len(string)):
            if functions.Identifier.is_mode(string[i]):
                mode = translator.alias.mode(string[i])
                mode_found = True

            elif functions.Identifier.is_int(string[i]):
                osu_id = int(string[i])

            elif functions.Identifier.is_osu_user_url(string[i]):
                osu_id = functions.Converter.url_to_osu_user(string[i]).userId

        if osu_id == "":
            if self.user['osu_id'] != 0:
                osu_id = self.user['osu_id']
                if not mode_found:
                    mode = self.user['mode']

        recent_play = self._api.get_user_recent(user_id=osu_id, mode=mode)
        if functions.Converter.find_username(self.message.content) is None:
            current_user = self._api.get_user(user_id=osu_id, mode=mode)
        user_image_url = self._api.get_user_image_url(osu_id)

        if current_user is None:
            await self.message.channel.send(s_user_not_found)
            return

        if recent_play is None:
            await self.message.channel.send(s_no_recent_play)
            return

        name = f"{current_user.username}{s_of_recent}"

        colour = functions.HelpDiscord.get_my_colour(self.client, self.message.channel)

        description = ""
        
        beatmap = self._api.get_beatmaps(recent_play[0].beatmapId, mode=mode, mods=recent_play[0].enabledMods)
        thumbnail_url = self._api.get_beatmap_thumb_url(beatmap.beatmapsetId)

        description += self._helpOsu.add_string_play(recent_play[0], mode=mode, language=self.user['language'], beatmap=beatmap)

        hits_played = self._helpOsu.get_total_hits(mode, recent_play[0])
        total_hits = beatmap.countNormal + beatmap.countSlider + beatmap.countSpinner
        completion = round(hits_played / total_hits * 100, 2)

        footer = f"{completion}% {s_completed}"

        embed = discord.Embed(description=description, colour=colour)
        embed.set_author(name = name, icon_url=user_image_url)
        embed.set_thumbnail(url=thumbnail_url)
        embed.set_footer(text=footer)

        await self.message.channel.send(embed=embed)

        return

    async def top(self, string):
        f = open('translation/'+self.user['language']+'.json')
        trans = json.load(f)['top']
        f.close()
        f = open('translation/variables.json')
        trans_var = json.load(f)
        f.close()
        
        s_mode = trans['mode']
        s_osu_id = trans['osu_id']
        s_or = trans['or']
        s_username = trans['username']
        s_osu_user_url = trans['osu_user_url']
        s_osu_user_not_set = trans['osu_user_not_set']
        s_of_top = trans['of_top'] 
        s_no_top_play = trans['no_top_play']
        s_user_not_found = trans['user_not_found']
        s_completed = trans['completed']

        mode = 0
        osu_id = 0
        mode_found = False
        limit = 5

        if functions.Converter.find_username(self.message.content) is not None:
            current_user = self._api.get_user(username=functions.Converter.find_username(self.message.content))

            if current_user is None:
                await self.message.channel.send(s_user_not_found)
                return

            osu_id = current_user.userId

        for i in range(len(string)):
            if functions.Identifier.is_mode(string[i]):
                mode = translator.alias.mode(string[i])
                mode_found = True

            elif functions.Identifier.is_int(string[i]):
                osu_id = int(string[i])

            elif functions.Identifier.is_osu_user_url(string[i]):
                osu_id = functions.Converter.url_to_osu_user(string[i]).userId

        if osu_id == 0:
            if self.user['osu_id'] != 0:
                osu_id = self.user['osu_id']
                if not mode_found:
                    mode = self.user['mode']

        top_plays = self._api.get_user_best(user_id=osu_id, mode=mode, limit=limit)
        if functions.Converter.find_username(self.message.content) is None:
            current_user = self._api.get_user(user_id=osu_id, mode=mode)
        user_image_url = self._api.get_user_image_url(osu_id)

        if current_user is None:
            await self.message.channel.send(s_user_not_found)
            return

        if top_plays is None:
            await self.message.channel.send(s_no_top_play)
            return

        name = f"{current_user.username}{s_of_top}"

        colour = functions.HelpDiscord.get_my_colour(self.client, self.message.channel)

        description = ""

        for i in range(limit):
            beatmap = self._api.get_beatmaps(top_plays[i].beatmapId, mode=mode, mods=top_plays[i].enabledMods)
        
            description += self._helpOsu.add_string_play(top_plays[i], mode=mode, language=self.user['language'], beatmap=beatmap)

        embed = discord.Embed(description=description, colour=colour)
        embed.set_author(name = name, icon_url=user_image_url)

        await self.message.channel.send(embed=embed)

        return

    async def compare(self, string):
        f = open('translation/'+self.user['language']+'.json')
        trans = json.load(f)['compare']
        f.close()
        f = open('translation/variables.json')
        trans_var = json.load(f)
        f.close()

        s_mode = trans['mode']
        s_osu_id = trans['osu_id']
        s_or = trans['or']
        s_username = trans['username']
        s_osu_user_url = trans['osu_user_url']
        s_osu_user_not_set = trans['osu_user_not_set']
        s_of = trans['of']
        s_play = trans['play'] 
        s_user_not_found = trans['user_not_found']
        s_no_play = trans['no_play']

        beatmap_id = 0
        osu_id = 0

        for temp in string:
            if functions.Identifier.is_int(temp):
                beatmap_id = int(temp)
            elif functions.Identifier.is_beatmap_url(temp):
                beatmap_id = functions.Converter.url_to_beatmap(temp).beatmapId

        if beatmap_id == 0:
            channel = preferences.load_channel(self.message.channel)
            if channel is None:
                await self.missing(["beatmap id"])
                return
            beatmap_id = channel['recent_beatmap_id']

        mode = self._api.get_beatmaps(beatmap_id).mode

        if functions.Converter.find_username(self.message.content) is not None:
            current_user = self._api.get_user(username=functions.Converter.find_username(self.message.content))

            if current_user is None:
                await self.message.channel.send(s_user_not_found)
                return

            osu_id = current_user.userId

        for temp in string:
            if functions.Identifier.is_mode(temp):
                mode = translator.alias.mode(temp)

        for i in range(len(string)):
            if functions.Identifier.is_int(string[i]):
                osu_id = int(string[i])

            elif functions.Identifier.is_osu_user_url(string[i]):
                osu_id = functions.Converter.url_to_osu_user(string[i]).userId

        if osu_id == 0:
            if self.user['osu_id'] != 0:
                osu_id = self.user['osu_id']
                
        playdatas = self._api.get_scores(beatmap_id, user_id = osu_id, mode = mode)

        if functions.Converter.find_username(self.message.content) is None:
            current_user = self._api.get_user(user_id=osu_id, mode=mode)
        user_image_url = self._api.get_user_image_url(osu_id)

        if current_user is None:
            await self.message.channel.send(s_user_not_found)
            return

        if playdatas is None:
            await self.message.channel.send(s_no_play)
            return
        
        beatmap = self._api.get_beatmaps(beatmap_id)
        thumbnail_url = self._api.get_beatmap_thumb_url(beatmap.beatmapsetId)
        beatmap_url = functions.Converter.beatmap_to_url(beatmap)

        name = f"{current_user.username} {s_of} [{beatmap.title} [{beatmap.version}]] {s_play}"
        colour = functions.HelpDiscord.get_my_colour(self.client, self.message.channel)
        description = ""

        for playdata in playdatas:
            beatmap = self._api.get_beatmaps(beatmap_id, mode=mode, mods=playdata.enabledMods)
            description += self._helpOsu.add_string_play(playdata, mode=mode, language=self.user['language'], beatmap=beatmap)

        embed = discord.Embed(description=description, colour=colour)
        embed.set_author(name = name, icon_url=user_image_url)
        embed.set_thumbnail(url=thumbnail_url)

        await self.message.channel.send(embed=embed)

        return

    async def missing(self, string_list):

        f = open('translation/'+self.user['language']+'.json')
        trans = json.load(f)['com_missing']
        f.close()

        s_missing_arguments = trans['missing_arguments']

        arguments = ""
        for i in range(len(string_list)):
            arguments += string_list[i]
            if i == len(string_list) - 1:
                break
            arguments += ", "

        await self.message.channel.send(f"{s_missing_arguments}: {arguments}")

    async def wrong(self, string_list):

        f = open('translation/'+self.user['language']+'.json')
        trans = json.load(f)['com_wrong']
        f.close()

        s_wrong_arguments = trans['wrong_arguments']

        arguments = ""
        for i in range(len(string_list)):
            arguments += string_list[i]
            if i == len(string_list) - 1:
                break
            arguments += ", "

        await self.message.channel.send(f"{s_wrong_arguments}: {arguments}")