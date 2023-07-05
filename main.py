from src.util.pyqt_geo_manager import *
from src.util.automaticScript import *
import threading
import socket
import csv
import datetime
import sys
import io


class OutputLogger(io.TextIOBase):
    def __init__(self, csv_file_name):
        self.csv_file_name = csv_file_name

    def write(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            'timestamp': timestamp,
            'type': 'print',
            'data': message.rstrip()
        }
        with open(self.csv_file_name, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['timestamp', 'type', 'data'])
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(data)

    def flush(self):
        pass


def setup_output_logging(csv_file_name):
    output_logger = OutputLogger(csv_file_name)
    sys.stdout = output_logger
    sys.stderr = output_logger


def sub_processes(tar, nm):
    background_thread = threading.Thread(target=tar)
    background_thread.daemon = True
    background_thread.start()
    print(f"{nm} is running...")
    return background_thread


if __name__ == '__main__':
    # Logger
    # setup_output_logging(csv_file_name=config_variables["vers"]["logger"])

    # subprocess - automaticScripts_main
    bkg_thread = sub_processes(tar=automaticScript_main, nm='automaticScript_main')
    # BUG: csd
    # HACK: cdosvjkmldf
    json_str = json.dumps(config_variables, indent=4)
    print(json_str)

    execute_app()

    bkg_thread.join()
