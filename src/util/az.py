from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
import pandas as pd
from io import BytesIO
from src.util.importConf import*

# Load the configuration variables
config_variables = load_config()
azure_config = config_variables['azure_config']
# Now you can access the elements in the config dictionary:
# azure_config = config['azure']
# indexes_config = config['indexes_config']


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


def FAZUpload():
    # with open('config/conf.yaml', 'r') as f:
    #     config = yaml.safe_load(f)
    # # azure_config = config['azure']
    try:
        connect_str = azure_config['connect_str']
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = azure_config['container_name']

        container_client = blob_service_client.get_container_client(container_name)
        base_blob_name = azure_config['blob_name']

        existing_blobs = [blob.name for blob in container_client.list_blobs()]
        # Generate unique blob name
        blob_name = generate_unique_name(base_blob_name, existing_blobs)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        print("\nUploading to Azure Storage as blob:\n\t" + blob_name)
        # Upload the created file
        with open("data/uploads/press-state-history__From_2023-21-06_00-01-00_To_2023-21-06_15-54-00.csv",
                  "rb") as data:
            blob_client.upload_blob(data)

    except Exception as ex:
        print('Exception:')
        print(ex)


def FAZdownload():
    # with open('config/conf.yaml', 'r') as f:
    #     config = yaml.safe_load(f)
    # azure_config = config['azure']
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
        print('Exception:')
        print(ex)


def FAZstreamAzData():
    # with open('config/conf.yaml', 'r') as f:
    #     config = yaml.safe_load(f)
    # azure_config = config['azure']

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
