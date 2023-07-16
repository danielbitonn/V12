import json
import os
import sys
import traceback
import socket
from datetime import date
from config_manager import fjp
from src.util.azure import func_azure_container_connect


def auto_write_storage_containers_and_blobs_to_json():
    output_file_path = fjp()['azure']['output_json_path']
    output_file_json = fjp()['azure']['output_json_name']
    if not os.path.exists(output_file_path):
        os.makedirs(output_file_path)
    try:
        blob_service_client, container_client, container_name = func_azure_container_connect()  # return blob_service_client, container_client, container_name
    except Exception as ex:
        print(
            f"Exception: func_azure_container_connect, Connection has been failed: >>> {ex} >>> {traceback.extract_tb(list(sys.exc_info())[2])} >>> <{blob_service_client}><{container_client}><{container_name}>")

    # Get a list of containers in the storage account
    containers = []
    for container in blob_service_client.list_containers():
        container_name = container.name
        blobs = []
        for blob in blob_service_client.get_container_client(container_name).list_blobs():
            blobs.append(blob.name)
        containers.append({"container_name": container_name, "blobs": blobs})

    # Add "date" and "local_machine" keys at the beginning
    data = {
            "date": str(date.today()),
            "local_machine": socket.gethostname(),
            "containers": containers
            }
    # Check if the JSON file already exists
    if os.path.isfile(f'{output_file_path}{output_file_json}'):
        with open(f'{output_file_path}{output_file_json}', 'r+') as file:
            json_data = json.load(file)
            # Check if a record with the same date and local_machine already exists
            for index, record in enumerate(json_data):
                if record["date"] == data["date"] and record["local_machine"] == data["local_machine"]:
                    # Update the existing record
                    json_data[index] = data
                    break
            else:
                # Insert the new record at the beginning
                json_data.insert(0, data)
            # Seek to the beginning of the file and write the updated JSON data
            file.seek(0)
            json.dump(json_data, file, indent=4)
    else:
        # Write the data to a new JSON file
        with open(f'{output_file_path}{output_file_json}', "w") as file:
            json.dump([data], file, indent=4)
