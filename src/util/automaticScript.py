# from config_manager import *
from src.util.azure import *
# from azure.storage.blob import BlobServiceClient
# import json
from config_manager import *


def write_storage_containers_and_blobs_to_json(output_file_path, output_file_json):
    if not os.path.exists(output_file_path):
        os.makedirs(output_file_path)

    try:
        blob_service_client, container_client, container_name = func_azure_container_connect()  # return blob_service_client, container_client, container_name
    except Exception as ex:
        print(
            f">>> Connection Failed:\n>>>{ex}\n(func_azure_container_connect):\n{blob_service_client}\n{container_client}\n{container_name}\n")

    # Get a list of containers in the storage account
    containers = []
    for container in blob_service_client.list_containers():
        container_name = container.name
        blobs = []
        for blob in blob_service_client.get_container_client(container_name).list_blobs():
            blobs.append(blob.name)
        containers.append({"container_name": container_name, "blobs": blobs})

    # Write the containers and blob names to a JSON file
    with open(f'{output_file_path}{output_file_json}', "w") as file:
        json.dump(containers, file, indent=4)


def automaticScript_main():
    # Load the configuration variables
    conf_var = func_read_config()
    azure_conf = conf_var['azure']
    try:
        write_storage_containers_and_blobs_to_json(output_file_path=azure_conf['output_json_path'],
                                                   output_file_json=azure_conf['output_json_name'])
    except Exception as ex:
        print(f">>> Writing Failed:\n>>>{ex}\n(write_storage_containers_and_blobs_to_json)")
