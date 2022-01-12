# -*- coding: utf-8 -*-

import os

import json

class alias(object):
    def command(string):
        string = string.lower()

        f = open(os.getcwd()+'/translation/commands.json')
        command_list = json.load(f)
        f.close()

        for key, value in command_list.items():
            if string in value['alias']:
                return key
        
        return

    def mode(string):
        string = string.lower()

        f = open(os.getcwd()+'/translation/general.json')
        modes = json.load(f)['mode']
        f.close()

        for key, value in modes.items():
            if string in value:
                return int(key)

        return
    
    def language(string):
        string = string.lower()

        f = open(os.getcwd()+'/translation/general.json')
        modes = json.load(f)['language']
        f.close()

        for key, value in modes.items():
            if string in value:
                return key

        return

    def property(string):
        string = string.lower()
        f = open(os.getcwd()+'/translation/general.json')
        properties = json.load(f)['property']
        f.close()

        for key, value in properties.items():
            if string in value:
                return key

        return

class translate(object):
    def script(language):
        f = open(os.getcwd()+'/translation/'+language+'.json')
        translation = json.load(f)
        f.close()

        return translation

    def command(language):
        string = string.lower()

        f = open(os.getcwd()+'/translation/commands.json')
        command_list = json.load(f)
        f.close()

        for key, value in command_list.items():
            if string in value['alias']:
                return key
        
        return

    def mode(string):
        string = string.lower()

        f = open(os.getcwd()+'/translation/general.json')
        modes = json.load(f)['mode']
        f.close()

        for key, value in modes.items():
            if string in value:
                return int(key)

        return
    
    def language(string):
        string = string.lower()

        f = open(os.getcwd()+'/translation/general.json')
        modes = json.load(f)['language']
        f.close()

        for key, value in modes.items():
            if string in value:
                return key

        return

    def property(string):
        string = string.lower()
        f = open(os.getcwd()+'/translation/general.json')
        properties = json.load(f)['property']
        f.close()

        for key, value in properties.items():
            if string in value:
                return key

        return