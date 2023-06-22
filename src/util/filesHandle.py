import os
import fnmatch

'''
Using:
from src.util.filesHandle import *
path = find_rel_path(file_name="file_name.extention")
'''
def find_root(root_name='README.md'):
    path = os.path.realpath(os.getcwd())
    while True:
        if root_name in os.listdir(path):
            return path
        else:
            new_path = os.path.dirname(path)
            if new_path == path:  # We've hit the top level
                raise Exception(f"Couldn't find {root_name} in any parent directories.")
            path = new_path


def find_rel_path(file_name):
    script_dir = os.path.dirname(os.path.abspath(find_root()))

    for dirpath, dirs, files in os.walk(script_dir):
        for filename in fnmatch.filter(files, file_name):
            filepath = os.path.join(dirpath, filename)
            return filepath
