import subprocess
import socket
import os

from config_manager import *

config_variables = func_read_config()
freeCMD_config = config_variables['freecmd']
azure_config = config_variables['azure']


def func_run_free_cmd_command():
    try:
        cmd = f"{freeCMD_config['comm']}"
        subprocess.run(["cmd.exe", "/c", cmd], shell=True)

    except Exception as ex:
        print(f'\nException: func_run_free_cmd_command Failed with {freeCMD_config["comm"]}\n')
        print(ex)


def func_rename_files_get_sn(dir_path):
    # Adding SN
    SN = socket.getfqdn()
    # List all files in the directory
    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    # Iterate over each file
    for filename in files:
        if azure_config['prssSNSeparator'] not in filename:
            # Construct new filename
            new_filename = f"{SN}{azure_config['prssSNSeparator']}{filename}"

            # Construct full file paths
            old_filepath = os.path.join(dir_path, filename)
            new_filepath = os.path.join(dir_path, new_filename)

            # Rename the file
            os.rename(old_filepath, new_filepath)
            print(f"{old_filepath} - renamed to:\n{new_filepath}\n")

    return
