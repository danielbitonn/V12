from src.util.pyqt_geo_manager import *
from config_manager import *
from src.util.utilitiesFunctions import *
# from src.util.tk_manager import*
import socket

if __name__ == '__main__':
    # Load the configuration variables
    config_variables = func_read_config()
    json_str = json.dumps(config_variables, indent=4)
    print(json_str)
    print(socket.getfqdn())
    execute_app()
