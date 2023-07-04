from src.util.azure import *
from src.util.pyqt_geo_manager import *
from src.util.utilitiesFunctions import *
import subprocess


def button_switch_case(case_value):
    switcher = {
        1: handle_case_1,
        2: handle_case_2,
        3: handle_case_3,
        4: handle_case_4,
        5: handle_case_5,
        6: handle_case_6,
        7: handle_case_7,
        8: handle_case_8,
    }
    # Get the function from switcher dictionary with the case_value as a key
    # (default to handle_default function if case_value not found)
    handler = switcher.get(case_value, handle_default)
    handler()
    print(f"Button {case_value} was clicked!!!")
    return


################################################################################################################################
def handle_case_1():
    """
    Execute direct .bat files which are exporting data using esExporter.exe, then pull files to azure
    """
    print("\n### This is case 1 ###\n")
    case_1_path = path_config['PushExpDataPathRel']
    try:
        func_execute_bat_files()
        print(f'\nfunc_execute_bat_files Succeed!!!')
    except Exception as ex:
        print(f'Exception: func_execute_bat_files Failed')
        print(ex)

    try:
        func_rename_files_get_sn(dir_path=case_1_path)
        print(f'\nfunc_rename_files_get_sn Succeed!!!')
    except Exception as ex:
        print(f'Exception: func_rename_files_get_sn Failed')
        print(ex)

    try:
        func_azure_uploader(upload_source_path=case_1_path)
        print(f'\nfunc_azure_uploader Succeed!!!')
    except Exception as ex:
        print(f'Exception: func_azure_uploader Failed')
        print(ex)
        return

    print("\n\nCase 1 Done")
    return


def handle_case_2():
    print("\n### This is case 2 ###\n")
    downPath = os.path.join(path_config['PullExpDataPathRel'], func_remove_symbols(socket.getfqdn()))
    print(downPath)
    func_azure_downloader(downloadedFilesPath=downPath)
    print("\n\nCase 2 Done")
    return


def handle_case_3():
    """
    stream data from cloud directly to dataframe
    """
    print("\n### This is case 3 ###\n")
    func_azure_streaming()

    print("\n\nCase 3 Done")
    return


def handle_case_4():
    """
    Execute CMD command similar as the .bat files
    which are exporting data using esExporter.exe
    No - uploaded!
    """
    case_4_path = path_config['PushExpDataPathRelCMD']

    print("\n### This is case 4 ###\n")
    try:
        func_press_direct_cmd_exporter()
        print(f'\nfunc_press_direct_cmd_exporter Completed!!!')
    except Exception as ex:
        print(f'\nException: func_press_direct_cmd_exporter Failed')
        print(ex)

    try:
        func_rename_files_get_sn(dir_path=case_4_path)
        print(f'\nfunc_rename_files_get_sn Succeed!!!')
    except Exception as ex:
        print(f'Exception: func_rename_files_get_sn Failed')
        print(ex)

    try:
        func_azure_uploader(upload_source_path=case_4_path)
        print(f'\nfunc_azure_uploader Succeed!!!')
    except Exception as ex:
        print(f'Exception: func_azure_uploader Failed')
        print(ex)

    print("\n\nCase 4 Done")
    return


def handle_case_5():
    print("\n### This is case 5 ###\n")
    try:
        func_azure_uploader(upload_source_path=path_config['PushExpDataPathRel'])
        print(f"\nfunc_azure_uploader with {path_config['PushExpDataPathRel']} Completed!!!")
    except Exception as ex:
        print(f'Exception: func_azure_uploader Failed')
        print(ex)
        return

    try:
        func_azure_uploader(upload_source_path=path_config['PushExpDataPathRelCMD'])
        print(f"\nfunc_azure_uploader with {path_config['PushExpDataPathRelCMD']} Completed!!!")
    except Exception as ex:
        print(f'Exception: func_azure_uploader Failed')
        print(ex)
        return

    print("\n\nCase 5 Done")
    return


def handle_case_6():
    func_run_free_cmd_command()
    print("This is case 6")

    print("\n\nCase 6 Done")
    return


def handle_case_7():
    print("This is case 7")

    subprocess.call(['python', 'src/gui_creator/Sandbox_timeline_report.py'])
    print("\n\nCase 7 Done")
    return


def handle_case_8():
    print("This is case 8")
    subprocess.call(['python', 'src/gui_creator/SandBox_file.py'])
    print("\n\nCase 8 Done")
    return


def handle_default():
    print("This is the default case")
    return "This is the default case"
