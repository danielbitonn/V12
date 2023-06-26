import datetime
import subprocess
import sys
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import pandas as pd
from io import BytesIO
import os
from config_manager import *

# Load the configuration variables
config_variables = read_config()
azure_config = config_variables['azure']
indexes_config = config_variables['indexes']
path_config = config_variables['paths']
batsFiles_config = config_variables['batsFiles']


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


def load_data_from_blob(blob_service_client, container_name, blob_name):
    blob_client = blob_service_client.get_blob_client(container_name, blob_name)
    data = blob_client.download_blob().readall()
    df = pd.read_csv(BytesIO(data))
    return df


def func_press_export_data():
    for src in indexes_config:
        try:
            from_time = sys.argv[1] if len(sys.argv) > 1 else '00:01'  # check for command line argument
            now = datetime.datetime.now()  # get current date and time
            mydate = now.strftime('%Y-%m-%d')  # format date as YYYY-MM-DD
            # format time as HH:MM
            mytime = now.strftime('%H:%M').zfill(5)  # zfill ensures leading zero
            # TODO: check if the fixed is working!
            nameable_time2 = mytime.replace(':', ':')  # format time as HH.MM
            nameable_from = from_time.replace(':', ':')  # format from_time as HH.MM

            # create directory if it doesn't exist
            if not os.path.exists(path_config['exportedData']):
                os.makedirs(path_config['exportedData'])

            # execute CMD program
            # cmd = f'S:\\Press\\PressTools.EsExporter.exe -i {indexes_config[src]} -f {mydate}T{nameable_from} -t {mydate}T{nameable_time2} -o C:\\ExportedEsData\\{src}'
            cmd = f"{path_config['PressEsExporter']} -i {indexes_config[src]} -f {mydate}T{nameable_from} -t {mydate}T{nameable_time2} -o {path_config['exportedData']}{src}.csv"
            print(cmd)
            subprocess.call(cmd, shell=True)

        except Exception as ex:
            print('Exception: func_export_data Failed')
            print(ex)


def func_azure_uploader():
    try:
        connect_str = azure_config['connect_str']
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = azure_config['container_name']

        container_client = blob_service_client.get_container_client(container_name)
        existing_blobs = [blob.name for blob in container_client.list_blobs()]

        for fileName in indexes_config:
            base_blob_name = fileName
            # Generate unique blob name
            blob_name = generate_unique_name(base_blob_name, existing_blobs)
            print("\nUploading to Azure Storage as blob:\n\t" + blob_name)

            # Upload the created file
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            with open(f"{path_config['exportedData']}{base_blob_name}.csv", "rb") as data:
                blob_client.upload_blob(data)

    except Exception as ex:
        print('Exception: func_azure_uploader Failed')
        print(ex)


def func_azure_downloader():
    try:
        target_dir = 'data/downloads/'
        connect_str = azure_config['connect_str']
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = azure_config['container_name']
        container_client = blob_service_client.get_container_client(container_name)
        blob_list = container_client.list_blobs()
        for blob in blob_list:
            if not os.path.splitext(blob.name)[1] == '.csv':
                download_path = os.path.join(target_dir, f"{blob.name}{'.csv'}")
            else:
                download_path = os.path.join(target_dir, blob.name)
                # if not os.path.exists(download_path):
                print(f"Downloading blob to {download_path}")
                blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob.name)
                with open(download_path, "wb") as download_file:
                    data = blob_client.download_blob().readall()
                    download_file.write(data)
    except Exception as ex:
        print('Exception: func_azure_downloader Failed')
        print(ex)


def func_azure_streaming():
    # TODO: handle-next phase
    try:
        connect_str = azure_config['connect_str']
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = azure_config['container_name']
        blob_name = azure_config['blob_name']

        df = load_data_from_blob(blob_service_client, container_name, blob_name)
        print(df)

    except Exception as ex:
        print('Exception:')
        print(ex)


def func_azure_uploader_2(blob_name):
    try:
        connect_str = azure_config['connect_str']
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = azure_config['container_name']

        # Upload the created file
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        with open(f"S:\\_db_\\V12App\\data\\{blob_name}", "rb") as data:
            blob_client.upload_blob(data)
    except Exception as ex:
        print('Exception: func_azure_uploader_2 !!!!! Failed')
        print(ex)


def func_execute_bat_files():
    """ .bat files executes """
    for batFile in batsFiles_config:
        try:
            subprocess.run(["cmd.exe", "/c", batsFiles_config[batFile]], shell=True)
            # TODO: handle this function to upload by name
            # func_azure_uploader_2()
        except Exception as ex:
            print(f'Exception: func_execute_bat_files Failed with {batsFiles_config[batFile]}')
            print(ex)
