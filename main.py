from src.util.pyqt_geo_manager import *
from config_manager import *

# from src.util.tk_manager import*


if __name__ == '__main__':
    # Load the configuration variables
    config_variables = func_read_config()
    json_str = json.dumps(config_variables, indent=4)
    print(json_str)
    execute_app()
