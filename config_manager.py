import json


def func_read_config():
    with open('conf.json', 'r') as config_file:
        conf = json.load(config_file)
    return {
        'azure': conf['azure'],
        'indexes': conf['indexes'],
        'paths': conf['paths'],
        'batsFiles': conf['batsFiles'],
        'cmdCommands': conf['cmdCommands'],
        'vers': conf['vers'],
        'freecmd': conf['freecmd'],
        'presses': conf['presses']
    }
