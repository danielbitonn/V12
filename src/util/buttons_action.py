

from src.AutomationScriptsDir.auto_copy_sqlDB import *
from src.AutomationScriptsDir.auto_daily_report_beta import *
from src.AutomationScriptsDir.auto_df_combinatoin import *
from src.AutomationScriptsDir.auto_sql_handling_system import auto_sql_handling_system
from src.util.azure import *
from src.util.pyqt_geo_manager import *
from src.util.utilitiesFunctions import *
import subprocess


def button_switch_case(case_value):
    switcher = {
        1: handle_case_1,
        2: handle_case_2,
        3: handle_case_3,
        # 4: handle_case_4,
        # 5: handle_case_5,
        # 6: handle_case_6,
        # 7: handle_case_7,
        # 8: handle_case_8,
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
    print(f"### This is case 1 ### >>> {traceback.extract_tb(list(sys.exc_info())[2])}")
    # path: data_push_exported_data>bxxxxxxxx>yyyy-mm-dd
    case_1_path = f"{path_config['PushExpDataPathRel']}\\{func_read_log_json()['current_press']}\\{datetime.datetime.now().strftime('%Y-%m-%d')}\\"
    try:
        bkg_thread_auto_copy_sqlDB = func_sub_processes(tar=auto_copy_sqlDB(dir_path_out=case_1_path), nm='auto_copy_sqlDB')
    except Exception as ex:
        print(f"Exception: auto_copy_sqlDB has been failed: >>> {ex} >>> {traceback.extract_tb(list(sys.exc_info())[2])}")

    try:
        bkg_thread_func_execute_bat_files = func_sub_processes(tar=func_execute_bat_files(dir_path_output=case_1_path), nm='func_execute_bat_files')
    except Exception as ex:
        print(f"Exception: func_execute_bat_files has been failed: >>> {ex} >>> {traceback.extract_tb(list(sys.exc_info())[2])}")

    # Waiting for those threads
    print("Exporting...")
    bkg_thread_auto_copy_sqlDB.join()
    bkg_thread_func_execute_bat_files.join()

    # while bkg_thread_auto_copy_sqlDB.is_alive() or bkg_thread_func_execute_bat_files.is_alive():
    #     print("...")
    #     time.sleep(1)

    try:
        func_rename_files_get_sn(dir_path=case_1_path)
    except Exception as ex:
        print(f"Exception: func_rename_files_get_sn has been failed: >>> {ex} >>> {traceback.extract_tb(list(sys.exc_info())[2])}")

    # Combine all Files into 1 csv file and delete with (fjp()['azure']['combineSeperator']) then delete the rest
    try:
        combined_df = func_collect_and_combine_csv_files(directory=case_1_path)
        print(combined_df)
    except Exception as ex:
        print(f"Exception: func_collect_and_combine_csv_files has been failed: >>> {ex} >>> {traceback.extract_tb(list(sys.exc_info())[2])}")

    try:
        func_azure_uploader(upload_source_path=case_1_path)
        print(f'>>>func_azure_uploader Succeed!!!')
    except Exception as ex:
        print(f"Exception: func_azure_uploader has been failed: >>> {ex} >>> {traceback.extract_tb(list(sys.exc_info())[2])}")
        return


    print(f"### Case 1 Done ### >>> {traceback.extract_tb(list(sys.exc_info())[2])}")
    return


def handle_case_2():
    print(f"### This is case 2 ### >>> {traceback.extract_tb(list(sys.exc_info())[2])}")
    try:
        case_2_path = f"{path_config['PullExpDataPathRel']}{fjp(jsname='log.json')['current_press']}"
        # Downloading files
        bkg_thread_func_sub_processes = func_sub_processes(tar=func_azure_downloader(downloadedFilesPath=case_2_path), nm='func_azure_downloader')
        bkg_thread_func_sub_processes.join()
    except Exception as ex:
        print(f"Exception: func_azure_downloader has been failed: >>> {ex} >>> {traceback.extract_tb(list(sys.exc_info())[2])}")

    try:
        pull_last_date_path = func_get_latest_folder(case_2_path)
    except Exception as ex:
        print(f"Exception: func_get_latest_folder has been failed: >>> {ex} >>> {traceback.extract_tb(list(sys.exc_info())[2])}")

    try:
        bkg_thread_auto_sql_handling_system = func_sub_processes(tar=auto_sql_handling_system(sub_path=pull_last_date_path), nm='auto_sql_handling_system')
        bkg_thread_auto_sql_handling_system.join()
    except Exception as ex:
        print(
            f"Exception: auto_sql_handling_system has been failed: >>> {ex} >>> {traceback.extract_tb(list(sys.exc_info())[2])}")


    print(f"### Case 2 Done ### >>> {traceback.extract_tb(list(sys.exc_info())[2])}")
    return


def handle_case_3():
    print(f"### This is case 3 ### >>> {traceback.extract_tb(list(sys.exc_info())[2])}")
    try:
        func_run_exe(filepath=f'{fjp()["paths"]["exe_comm"]}')
    except Exception as ex:
        print(ex)
    print(f"### Case 3 Done ### >>> {traceback.extract_tb(list(sys.exc_info())[2])}")
    return


# def handle_case_4():
#     """
#     Execute CMD command similar as the .bat files
#     which are exporting data using esExporter.exe
#     No - uploaded!
#     """
#     case_4_path = path_config['PushExpDataPathRelCMD']
#
#     print("\n### This is case 4 ###\n")
#     try:
#         func_press_direct_cmd_exporter()
#         print(f'\nfunc_press_direct_cmd_exporter Completed!!!')
#     except Exception as ex:
#         print(f'\nException: func_press_direct_cmd_exporter Failed')
#         print(ex)
#
#     try:
#         func_rename_files_get_sn(dir_path=case_4_path)
#         print(f'\nfunc_rename_files_get_sn Succeed!!!')
#     except Exception as ex:
#         print(f'Exception: func_rename_files_get_sn Failed')
#         print(ex)
#
#     try:
#         func_azure_uploader(upload_source_path=case_4_path)
#         print(f'\nfunc_azure_uploader Succeed!!!')
#     except Exception as ex:
#         print(f'Exception: func_azure_uploader Failed')
#         print(ex)
#
#     print("\n\nCase 4 Done")
#     return
#
#
# def handle_case_5():
#     print("\n### This is case 5 ###\n")
#     try:
#         func_azure_uploader(upload_source_path=path_config['PushExpDataPathRel'])
#         print(f"\nfunc_azure_uploader with {path_config['PushExpDataPathRel']} Completed!!!")
#     except Exception as ex:
#         print(f'Exception: func_azure_uploader Failed')
#         print(ex)
#         return
#
#     try:
#         func_azure_uploader(upload_source_path=path_config['PushExpDataPathRelCMD'])
#         print(f"\nfunc_azure_uploader with {path_config['PushExpDataPathRelCMD']} Completed!!!")
#     except Exception as ex:
#         print(f'Exception: func_azure_uploader Failed')
#         print(ex)
#         return
#
#     print("\n\nCase 5 Done")
#     return
#
#
# def handle_case_6():
#     func_run_free_cmd_command()
#     print("This is case 6")
#
#     print("\n\nCase 6 Done")
#     return
#
#
# def handle_case_7():
#     """
#     stream data from cloud directly to dataframe
#     """
#     print("\n### This is case 7 ###\n")
#     func_azure_streaming()
#     print("\n\nCase 7 Done")
#     return
#
#
# def handle_case_8():
#     print("This is case 8")
#     subprocess.call(['python', 'src/gui_creator/SandBox_file.py'])
#     print("\n\nCase 8 Done")
#     return
#

def handle_default():
    print("This is the default case")
    return "This is the default case"
