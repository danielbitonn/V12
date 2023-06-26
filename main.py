import json
from src.util.pyqt_geo_manager import *
from config_manager import *

# from src.util.tk_manager import*


if __name__ == '__main__':
    # Load the configuration variables
    config_variables = read_config()
    print(config_variables)
    execute_app()
