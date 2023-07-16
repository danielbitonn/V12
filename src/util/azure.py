import pandas as pd
import subprocess
import datetime
import socket
import sys
import os

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from io import BytesIO

from src.util.utilitiesFunctions import *
from config_manager import *
from src.util.utilitiesFunctions import func_remove_symbols

# Load the configuration variables
config_variables = func_read_config()
azure_config = config_variables['azure']
indexes_config = config_variables['indexes']
path_config = config_variables['paths']
batsFiles_config = config_variables['batsFiles']
cmdCommands_config = config_variables['cmdCommands']


def func_azure_container_connect():
    try:
        connect_str = azure_config['connect_str']
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        container_name = func_remove_symbols(func_read_log_json()['current_press'])
        container_client = blob_service_client.get_container_client(container_name)

        try:
            # If the container does not exist, a ResourceNotFoundError will be thrown
            container_client.get_container_properties()
            print(f'{container_client} is exist!')
        except ResourceNotFoundError:
            print(f"{container_client} isn\'t exist >>> creating container!")
            # Create the container if it does not exist
            blob_service_client.create_container(container_name)

        print("\nCONNECT >>> CONTAINER >>> SUCCEED\n")

        return blob_service_client, container_client, container_name
    except Exception as ex:
        print(f">>>{ex}\n")


def func_load_data_from_blob(blob_service_client, container_name, blob_name):
    try:
        blob_client = blob_service_client.get_blob_client(container_name, blob_name)
        data = blob_client.download_blob().readall()
        df = pd.read_csv(BytesIO(data))
        return df
    except Exception as ex:
        print(f'\nException: func_load_data_from_blob Failed with {blob_name} due to:')
        print(ex)
        return pd.DataFrame()


def func_press_direct_cmd_exporter():
    exporter_path = path_config['PressEsExporter']
    output_path = path_config['PushExpDataPathRelCMD']
    mode_of_cmd_exporter = cmdCommands_config['exportMode']
    start_time = '00:01'

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    from_time = sys.argv[1] if len(sys.argv) > 1 else start_time  # check for command line argument for reference time!
    now = datetime.datetime.now()  # get current date and time
    mydate = now.strftime('%Y-%m-%d')  # format date as YYYY-MM-DD

    '''
    delta_hour = 2
    delta_min = 30
    time_before = now - datetime.timedelta(hours=delta_hour, minutes=delta_min)         # Subtract 2 hours and 31 minutes from the current time
    formatted_time = time_before.strftime('%H:%M').zfill(5)                             # Format the time in 'HH:MM' format and pad it to 5 characters with zeros if necessary
    nameable_from_relative = formatted_time.replace(':', '.')                           # format formatted_time as HH.MM
    '''

    mytime = now.strftime('%H:%M').zfill(5)  # format time as HH:MM, zfill ensures leading zero [03:15 AM == '03:15']
    nameable_time2 = mytime.replace(':', '.')  # format time as HH.MM
    nameable_from = from_time.replace(':', '.')  # format from_time as HH.MM

    for src in indexes_config:
        try:
            if len(mode_of_cmd_exporter):  # relative
                cmd = f"{exporter_path} -i {indexes_config[src]} -f {mydate}T{nameable_from} -t {mydate}T{nameable_time2} -o {output_path}"
            else:  # absolute
                cmd = f"{exporter_path} -i {indexes_config[src]} -f {cmdCommands_config['cmdMyDate']}T{cmdCommands_config['cmdFromTime']} -t {cmdCommands_config['cmdMyDate']}T{cmdCommands_config['cmdToTime']} -o {output_path}"

            print(f'extract {indexes_config[src]}...')
            subprocess.run(["cmd.exe", "/c", cmd], shell=True)

        except Exception as ex:
            print(f'\nException: func_export_data Failed with {src}')
            print(ex)


def func_azure_uploader(upload_source_path):
    if not os.path.exists(upload_source_path):
        os.makedirs(upload_source_path)

    file_list = [f for f in os.listdir(upload_source_path)
                 if os.path.isfile(os.path.join(upload_source_path, f))]
    print(f'Exported files:<{file_list}>')

    if len(file_list) > 0:
        try:
            blob_service_client, container_client, container_name = func_azure_container_connect()  # return blob_service_client, container_client, container_name
            print("connected")
        except Exception as ex:
            print(f"Exception: func_azure_uploader, Connection has been failed: >>> {ex} >>> {traceback.extract_tb(list(sys.exc_info())[2])} >>> <{blob_service_client}><{container_client}><{container_name}>")

        existing_blobs = [blob.name for blob in container_client.list_blobs()]
        for fileName in file_list:
            try:
                if fileName in existing_blobs:
                    # newfileName = func_generate_unique_name(fileName, existing_blobs, dirPath=upload_source_path)

                    container_client.delete_blob(fileName)
                    newfileName = fileName

                    print("INFO: Uploading to Azure Storage as blob:\t" + newfileName)
                    blob_client = blob_service_client.get_blob_client(container=container_name, blob=newfileName)
                    print(f"INFO: Uploading...<{newfileName}>")
                else:
                    blob_client = blob_service_client.get_blob_client(container=container_name, blob=fileName)
                    print(f"INFO: Uploading...<{fileName}>")

                try:
                    with open(f"{upload_source_path}\\{fileName}", "rb") as data:
                        blob_client.upload_blob(data)
                    print(f"INFO: Uploading done!")
                except Exception as ex:
                    print(f"Exception: Uploading phase has been failed: >>> {ex} >>> {traceback.extract_tb(list(sys.exc_info())[2])}")

            except Exception as ex:
                print(f"Exception: func_azure_uploader has been failed: >>> {ex} >>> {traceback.extract_tb(list(sys.exc_info())[2])}")
                pass
    else:
        print('WARNING: Exported files directory is empty!')


def func_azure_downloader(downloadedFilesPath):
    try:
        blob_service_client, container_client, container_name = func_azure_container_connect()     # return blob_service_client, container_client, container_name
    except Exception as ex:
        print(f"Exception: func_azure_downloader, Connection has been failed: >>> {ex} >>> {traceback.extract_tb(list(sys.exc_info())[2])} >>> <{blob_service_client}><{container_client}><{container_name}>")
    try:
        blob_list = container_client.list_blobs()
        for blob in blob_list:
            file_date = func_extract_date_from_filename(file_name=blob.name)
            case_2_sub_path = f"{downloadedFilesPath}\\{file_date}"
            if not os.path.exists(case_2_sub_path):
                os.makedirs(case_2_sub_path)

            if blob.name not in os.listdir(case_2_sub_path):
                download_path = os.path.join(case_2_sub_path, blob.name)
                print(f"Downloading {blob.name} to {case_2_sub_path}")
                blob_f = blob_service_client.get_blob_client(container=container_name, blob=blob.name)
                with open(download_path, "wb") as download_file:
                    data = blob_f.download_blob().readall()
                    download_file.write(data)
                print(f"{blob.name} has been downloaded!")
            else:
                print(f"{blob.name} already exist")
    except Exception as ex:
        print(f"Exception: func_azure_downloader (downloader) has been failed: >>> {ex} >>> {traceback.extract_tb(list(sys.exc_info())[2])}")


def func_azure_streaming():
    """
    stream data from cloud directly to dataframe
    :return: DFs
    """
    DFs = {}
    try:
        connect_str = azure_config['connect_str']
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = azure_config['container_name']

        # Check list of the files in the container
        container_client = blob_service_client.get_container_client(container_name)
        existing_blobs = [blob.name for blob in container_client.list_blobs()]
        print(existing_blobs)

    except Exception as ex:
        print('\nException: func_azure_streaming - Connection Client Failed')
        print(ex)

    try:
        current_date = datetime.datetime.now()
        formatted_date = current_date.strftime('%Y-%m-%d_%H-%M-%S')

        for file in existing_blobs:
            df_name = file.split(f"{azure_config['dfSeparator']}")[0]
            df_name = f'{df_name}_{formatted_date}'
            try:
                DFs[df_name] = func_load_data_from_blob(blob_service_client, container_name, file)
                print(DFs[df_name].head())
            except Exception as ex:
                print('\nException: func_azure_streaming - func_load_data_from_blob Failed due to:')
                print(ex)

    except Exception as ex:
        print('\nException: func_azure_streaming - Files Failed due to:')
        print(ex)


def func_execute_bat_files(dir_path_output):
    """ .bat files executes """
    print(f'#Subprocess Running... #func_execute_bat_files')
    if not os.path.exists(dir_path_output):
        os.makedirs(dir_path_output)

    # TODO: modify the bat file with the output directory == dir_path_output
    for batFile in batsFiles_config:
        try:
            subprocess.run(["cmd.exe", "/c", batsFiles_config[batFile]], shell=True)
            print(f'\nSuccess - {batsFiles_config[batFile]}\n')
        except Exception as ex:
            print(f'Exception: func_execute_bat_files Failed with {batsFiles_config[batFile]}')
            print(ex)
