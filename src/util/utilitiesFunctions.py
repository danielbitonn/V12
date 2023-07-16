import datetime
import logging
import subprocess
import socket
import os
import re
import threading

from config_manager import fjp
from src.AutomationScriptsDir.auto_copy_sqlDB import *
from src.util.azure import *

config_variables = fjp()
freeCMD_config = config_variables['freecmd']
azure_config = config_variables['azure']


def func_supporter_sn():
    with open('log.json', 'r') as log_file:
        log_app = json.load(log_file)
    return int(log_app['current_press'])


def func_run_free_cmd_command():
    try:
        cmd = f"{freeCMD_config['comm']}"
        subprocess.run(["cmd.exe", "/c", cmd], shell=True)

    except Exception as ex:
        print(f'\nException: func_run_free_cmd_command Failed with {freeCMD_config["comm"]}\n')
        print(ex)


def func_run_exe(filepath):
    try:
        subprocess.run(filepath)
        return "Success!"
    except Exception as ex:
        return ex


def func_rename_files_get_sn(dir_path):
    # Adding SN
    SN = fjp(jsname='log.json')['current_press']
    # List all files in the directory
    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    # Iterate over each file
    for filename in files:
        if azure_config['prssSNSeparator'] not in filename:
            # Construct new filename
            if func_extract_date_from_filename(filename) is None:
                new_filename = f"{SN}{azure_config['prssSNSeparator']}From_{datetime.datetime.now().strftime('%Y-%d-%m')}_{filename}"  # designated for the PressDB (because when it's download -the %m and %d will be swapped
            else:
                new_filename = f"{SN}{azure_config['prssSNSeparator']}{filename}"

            # Construct full file paths
            old_filepath = os.path.join(dir_path, filename)
            new_filepath = os.path.join(dir_path, new_filename)

            # Rename the file
            os.rename(old_filepath, new_filepath)
            # print(f"{old_filepath} - renamed to:\n{new_filepath}\n")
            print(f"Info:{old_filepath} - renamed to - {new_filepath}")
    print(f'#DONE# func_rename_files_get_sn')
    return


def func_remove_symbols(input_string):
    return ''.join(char.lower() for char in input_string if char.isalnum())


def func_generate_unique_name(base_name, existing_names, dirPath):
    base_name_without_ext = os.path.splitext(base_name)[0]
    extension = os.path.splitext(base_name)[1]

    if extension == '':
        base_name_without_ext = base_name
        extension = '.csv'

    unique_name = base_name

    i = 1
    while unique_name in existing_names:
        unique_name = f"{base_name_without_ext}_COPY({i}){extension}"
        i += 1

    return unique_name


def func_sub_processes(tar, nm):
    print(f"{nm} is running...")
    background_thread = threading.Thread(target=tar)
    background_thread.daemon = True
    background_thread.start()
    return background_thread


def func_get_latest_folder(path):
    folder_list = os.listdir(path)
    folder_list.sort(reverse=True)  # Sort the folder names in descending order
    for folder in folder_list:
        print(folder)
        if os.path.isdir(os.path.join(path, folder)):
            return folder
    return f"{datetime.datetime.now().strftime('%Y-%m-%d')}"


# TODO: if thread.is_alive(): - method to check if thread is alive.\
#  "thread" is the object the return from func_sub_processes!

def func_swap_day_month_in_date(date_string):
    if date_string:
        parts = date_string.split('-')
        if len(parts) == 3:
            parts[1], parts[2] = parts[2], parts[1]
            return '-'.join(parts)
    return date_string


def func_extract_date_from_filename(file_name):
    """Check if dates are exist in the name files"""
    match = re.search(r"\d{4}-\d{2}-\d{2}", file_name)
    if match:
        return func_swap_day_month_in_date(match.group())
    else:
        return None


def func_execute_python_file(filepath):
    with open(filepath, 'r') as file:
        exec(file.read())


class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.asctime = self.formatTime(record, self.datefmt)
        record.message = record.getMessage()
        record.name = record.name.replace(',', '').replace('"', '""')
        record.levelname = record.levelname.replace(',', '').replace('"', '""')
        record.message = record.message.replace(',', '').replace('"', '""')
        record.location = f"{record.filename}:{record.lineno}"
        s = '"%(asctime)s", "%(levelname)s", "%(location)s", "%(message)s"' % record.__dict__
        return s


def load_json(jsname):
    with open(jsname, "r") as file:
        return json.load(file)
