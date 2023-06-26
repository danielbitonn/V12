from src.util.azure import *
from src.util.stateDistribution import *


def button_switch_case(case_value):
    switcher = {
        1: handle_case_1,
        2: handle_case_2,
        3: handle_case_3,
        4: handle_case_4,
        5: handle_case_5,
        6: handle_case_6,
        7: handle_case_7,
    }
    # Get the function from switcher dictionary with the case_value as a key
    # (default to handle_default function if case_value not found)
    handler = switcher.get(case_value, handle_default)
    handler()
    print(f"Button {case_value} was clicked!!!")
    return
    # # Execute the function
    # return handler()


################################################################################################################################
def handle_case_1():
    try:
        func_execute_bat_files()
    except Exception as ex:
        print(f'Exception: func_execute_bat_files Failed')
        print(ex)
    try:
        func_azure_uploader()
    except Exception as ex:
        print(f'Exception: func_azure_uploader Failed')
        print(ex)
    print("This is case 1")
    return "This is case 1"


def handle_case_2():
    func_azure_downloader()
    print("This is case 2")
    return "This is case 2"


def handle_case_3():
    state_distribution_analysis()
    print("This is case 3")
    return "This is case 3"


def handle_case_4():
    func_azure_streaming()
    print("This is case 4")
    return "This is case 4"


def handle_case_5():
    try:
        func_execute_bat_files()
    except Exception as ex:
        print(f'Exception: func_execute_bat_files Failed')
        print(ex)
    print("This is case 5")
    return "This is case 5"


def handle_case_6():
    print("This is case 6")
    return "This is case 6"


def handle_case_7():
    print("This is case 7")
    return "This is case 7"


def handle_default():
    print("This is the default case")
    return "This is the default case"
