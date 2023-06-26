import os
import json


def read_config():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, 'conf.json')

    with open(config_path) as f:
        conf = json.load(f)
    return {
        'azure': conf['azure'],
        'indexes': conf['indexes'],
        'paths': conf['paths'],
        'batsFiles': conf['batsFiles']
    }
