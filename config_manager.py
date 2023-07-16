import json
import sys
import traceback



def func_read_config(jsname='conf.json'):
    with open(f'{jsname}', 'r') as config_file:
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


def func_read_log_json(jsname='log.json'):
    with open(f'{jsname}', 'r') as log_file:
        log_conf = json.load(log_file)
    return log_conf


def fjp(jsname='conf.json'):
    """Func json parameters"""
    try:
        with open(f'{jsname}', 'r') as fjp_file:
            fgps = json.load(fjp_file)
        return fgps
    except Exception as ex:
        print(f"Exception: fjp_function has been failed: >>> {ex} >>> {traceback.extract_tb(list(sys.exc_info())[2])}")

