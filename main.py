from src.util.filesHandle import find_rel_path
from src.util.pyqt_geo_manager import *
from src.util.utilitiesFunctions import *
import socket

if __name__ == '__main__':
    # Load the configuration variables
    # x = find_rel_path(file_name="SandBox_file.py")
    # subprocess.call(['python', x])
    pressSN = socket.getfqdn()
    config_variables = func_read_config()
    json_str = json.dumps(config_variables, indent=4)
    print(json_str)
    print(socket.getfqdn())
    execute_app()
