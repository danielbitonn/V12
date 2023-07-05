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


def func_read_log_json():
    with open('log.json', 'r') as log_file:
        log_conf = json.load(log_file)
    return log_conf
