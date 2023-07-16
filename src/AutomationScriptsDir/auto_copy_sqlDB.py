import os
import shutil
import sys
import traceback
from config_manager import *


def auto_copy_sqlDB(dir_path_out):
    ### dir_path_out: data_push_exported_data>bxxxxxxxx>yyyy-mm-dd
    print(f'#Running...# auto_copy_sqlDB #')
    try:
        # Specify source file and destination directory
        source_file = fjp(jsname='conf.json')["paths"]["pressDBpath"]  # 'S:\Press\PressDB.db'
        # Create the destination directory if it doesn't exist
        os.makedirs(dir_path_out, exist_ok=True)
        # Use shutil.copy() to copy the file
        shutil.copy(source_file, dir_path_out)

    except Exception as ex:
        # print(f">>> Function: auto_copy_sqlDB failed:\n>>> {ex}\n")
        print(f"Exception: auto_copy_sqlDB has been failed: >>> {ex} >>> {traceback.extract_tb(list(sys.exc_info())[2])}")

