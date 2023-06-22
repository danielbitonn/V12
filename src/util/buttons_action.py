from src.util.az import *
from src.dataAnalysis.stateDistribution import *


def button_action(butt_ID):
    switch_case(butt_ID)
    print(f"Button {butt_ID} was clicked!")


def switch_case(case_value):
    switcher = {
        1: handle_case_1,
        2: handle_case_2,
        3: handle_case_3,
        4: handle_case_4,
    }
    # Get the function from switcher dictionary with the case_value as a key
    # (default to handle_default function if case_value not found)
    handler = switcher.get(case_value, handle_default)
    # Execute the function
    return handler()


################################################################################################################################
def handle_case_1():
    FazUploading()
    print("This is case 1")
    return "This is case 1"


def handle_case_2():
    Fazdownloading()
    print("This is case 2")
    return "This is case 2"


def handle_case_3():
    state_distribution_analysis()
    print("This is case 3")
    return "This is case 3"


def handle_case_4():
    print("This is case 4")
    return "This is case 4"


def handle_default():
    print("This is the default case")
    return "This is the default case"
