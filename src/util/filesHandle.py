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


def get_abs_path(relative_path):
    """
    This function returns the absolute path of a file given its relative path from the project root directory.
    Args:
    relative_path (str): The relative path of the file from the project root directory.
    Returns:
    str: The absolute path of the file.
    """
    # Get the absolute path to the directory containing the currently executing script
    current_path = os.path.dirname(os.path.realpath(__file__))
    # Find the root directory of the project (assuming it's one level up from the current file)
    root_dir = os.path.dirname(current_path)
    root_dir = os.path.dirname(os.path.dirname(current_path))
    # Use os.path.join() to create the path to the file
    abs_path = os.path.join(root_dir, relative_path)

    return abs_path

