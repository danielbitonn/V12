from venv import logger

from src.util.tkinter_gui_manager import execute_app  # from src.util.pyqt_geo_manager import execute_app
from src.AutomationScriptsDir.auto_write_storage_containers_and_blobs_to_json import \
    auto_write_storage_containers_and_blobs_to_json
from src.util.utilitiesFunctions import *

import json
import datetime
import logging
import sys
import traceback


class LoggerWriter:
    def __init__(self, level, logger):
        self.level = level
        self.logger = logger

    def write(self, message):
        if message != '\n':
            self.logger.log(self.level, message)

    def flush(self):
        pass


def func_main_logger():
    """
    ### Now you can log messages like this:
    logger.info('This is an info message.')
    logger.error('This is an error message.')
    try:
        1 / 0
    except Exception as ex:
        logger.error(f"Exception: XXX_function has been failed: >>> {ex} >>> {traceback.extract_tb(list(sys.exc_info())[2])}")
    """
    # Logger Name
    logger_name = f'{fjp()["paths"]["PushExpDataPathRel"]}/{fjp(jsname="log.json")["current_press"]}/{load_json("log.json")["current_press"]}_{datetime.datetime.now().strftime("%Y-%m-%d")}_{load_json("conf.json")["logApp"]["AppLogName"]}'
    # Set up the logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    # Create a file handler
    handler = logging.FileHandler(f'{logger_name}.csv')
    handler.setLevel(logging.NOTSET)
    # Create a logging format
    formatter = CustomFormatter()
    handler.setFormatter(formatter)
    # Add the handlers to the logger
    logger.addHandler(handler)
    # Redirect stdout and stderr
    sys.stdout = LoggerWriter(logging.INFO, logger)
    sys.stderr = LoggerWriter(logging.ERROR, logger)


########################################################################################################################
########################################################################################################################
########################################################################################################################


if __name__ == '__main__':
    # TODO: Manage all folders and utilities files before running the main()
    # TODO: Delete folders which are older then 1 week.
    # TODO: Adding timeFrame availability
    # TODO:

    # TODO: move to the relevant place:
    if not os.path.exists('Images'):
        os.makedirs('Images')


    # 1. Logger Initializing
    func_main_logger()
    # 2. Main application
    bkg_thread_00 = func_sub_processes(tar=execute_app, nm='execute_app')

    # 3. Reading JSONs
    logger.info(fjp('conf.json'))
    logger.info(fjp('log.json')['current_press'])
    print(json.dumps(config_variables, indent=4))

    # 4. Getting Data from Azure
    try:
        bkg_thread_01 = func_sub_processes(tar=auto_write_storage_containers_and_blobs_to_json,
                                           nm='auto_write_storage_containers_and_blobs_to_json')
    except Exception as ex:
        print(f"Exception: auto_write_storage_containers_and_blobs_to_json has been failed: >>> {ex} >>> {traceback.extract_tb(list(sys.exc_info())[2])}")


    bkg_thread_01.join()
    bkg_thread_00.join()




