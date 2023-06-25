from src.util.az import *
from src.dataAnalysis.stateDistribution import *


def button_switch_case(case_value):
    switcher = {
        1: handle_case_1,
        2: handle_case_2,
        3: handle_case_3,
        4: handle_case_4,
        5: handle_case_5,
        6: handle_case_6,
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
    FAZUpload()
    print("This is case 1")
    return "This is case 1"


def handle_case_2():
    FAZdownload()
    print("This is case 2")
    return "This is case 2"


def handle_case_3():
    state_distribution_analysis()
    print("This is case 3")
    return "This is case 3"


def handle_case_4():
    FAZstreamAzData()
    print("This is case 4")
    return "This is case 4"


def handle_case_5():
    print("This is case 5")
    return "This is case 5"


def handle_case_6():
    print("This is case 6")
    return "This is case 6"


def handle_default():
    print("This is the default case")
    return "This is the default case"
