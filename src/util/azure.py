import datetime
import subprocess
import sys
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import pandas as pd
from io import BytesIO
import os
from config_manager import *

# Load the configuration variables
config_variables = func_read_config()
azure_config = config_variables['azure']
indexes_config = config_variables['indexes']
path_config = config_variables['paths']
batsFiles_config = config_variables['batsFiles']
cmdCommands_config = config_variables['cmdCommands']


# TODO: create 24h/48h/week extractor

def generate_unique_name(base_name, existing_names):
    base_name_without_ext = os.path.splitext(base_name)[0]
    extension = os.path.splitext(base_name)[1]

    if extension == '':
        base_name_without_ext = base_name
        extension = '.csv'

    unique_name = base_name
    i = 1

    while unique_name in existing_names:
        unique_name = f"{base_name_without_ext}_{i}{extension}"
        i += 1

    return unique_name


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
    output_path = path_config['PushExpDataPathRelCMD']
    # exporter_path = path_config['PressEsExporter']
    exporter_path = path_config['testEnv']

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    start_time = '00:01'

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

    # create directory if it doesn't exist
    # if not os.path.exists(path_config['exportedData']):
    #     os.makedirs(path_config['exportedData'])

    for src in indexes_config:
        try:
            # cmd = f'S:\\Press\\PressTools.EsExporter.exe -i {indexes_config[src]} -f {mydate}T{nameable_from} -t {mydate}T{nameable_time2} -o C:\\ExportedEsData'
            # cmd = f"{path_config['PressEsExporter']} -i {indexes_config[src]} -f {mydate}T{nameable_from} -t {mydate}T{nameable_time2} -o {path_config['exDataPath']}"
            # cmd = f"{exporter_path} -i {indexes_config[src]} -f {mydate}T{nameable_from} -t {mydate}T{nameable_time2} -o {output_path}"
            cmd = f"{cmdCommands_config['cmdExporterPath']} -i {indexes_config[src]} -f {cmdCommands_config['cmdMyDate']}T{cmdCommands_config['cmdFromTime']} -t {cmdCommands_config['cmdMyDate']}T{cmdCommands_config['cmdToTime']} -o {output_path}"

            print(f'extract {src} with:\n{cmd}\n')
            # subprocess.call(cmd, shell=True)
            subprocess.run(["cmd.exe", "/c", cmd], shell=True)

        except Exception as ex:
            print(f'\nException: func_export_data Failed with {src}\n')
            print(ex)


def func_azure_uploader(upload_source_path):
    file_list = [f for f in os.listdir(upload_source_path)
                 if os.path.isfile(os.path.join(upload_source_path, f))]
    print(f'Exported files:\n{file_list}')

    try:
        connect_str = azure_config['connect_str']
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = azure_config['container_name']

        # Check list of the files in the container
        # container_client = blob_service_client.get_container_client(container_name)
        # existing_blobs = [blob.name for blob in container_client.list_blobs()]

    except Exception as ex:
        print('\nException: func_azure_uploader - Connection Client Failed')
        print(ex)

    try:
        # for fileName in indexes_config:
        for fileName in file_list:
            # # Generate unique blob name - OLD
            # base_blob_name = fileName
            # blob_name = generate_unique_name(base_blob_name, existing_blobs)
            # print("\nUploading to Azure Storage as blob:\n\t" + blob_name)

            # # Upload the created file - OLD
            # blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            # with open(f"{path_config['exportedData']}{base_blob_name}.csv", "rb") as data:
            #     blob_client.upload_blob(data)

            blob_client = blob_service_client.get_blob_client(container=container_name, blob=fileName)
            with open(f"{upload_source_path}\\{fileName}", "rb") as data:
                blob_client.upload_blob(data)

    except Exception as ex:
        print('\nException: func_azure_uploader Failed in the Streaming-Downloading step')
        print(ex)


def func_azure_downloader():
    downloaded_file_path = path_config['PullExpDataPathRel']

    if not os.path.exists(downloaded_file_path):
        os.mkdir(downloaded_file_path)

    try:
        connect_str = azure_config['connect_str']
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = azure_config['container_name']

    except Exception as ex:
        print('\nException: func_azure_downloader - Connection Client Failed')
        print(ex)

    try:
        container_client = blob_service_client.get_container_client(container_name)
        blob_list = container_client.list_blobs()
        print(blob_list)

        for blob in blob_list:
            download_path = os.path.join(downloaded_file_path, blob.name)

            print(f"Downloading blob.name to {downloaded_file_path}")
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob.name)
            with open(download_path, "wb") as download_file:
                data = blob_client.download_blob().readall()
                download_file.write(data)
                # TODO: rename! based on blob.name and clean by the "__"
    except Exception as ex:
        print('Exception: func_azure_downloader Failed in download phase')
        print(ex)


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
            df_name = file.split("__")[0]
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


def func_execute_bat_files():
    """ .bat files executes """
    # TODO: verify where the bats saved
    if not os.path.exists(path_config['PushExpDataPathRel']):
        os.makedirs(path_config['PushExpDataPathRel'])

    for batFile in batsFiles_config:
        try:
            subprocess.run(["cmd.exe", "/c", batsFiles_config[batFile]], shell=True)
            # print(f'\nSuccess - {batsFiles_config[batFile]}\n')
        except Exception as ex:
            print(f'Exception: func_execute_bat_files Failed with {batsFiles_config[batFile]}')
            print(ex)
