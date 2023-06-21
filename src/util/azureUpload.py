import yaml
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

def FazureUploading():
    # Load the configuration data from the YAML file
    with open('config/conf.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Extract the Azure configuration details
    azure_config = config['azure']

    try:
        connect_str = azure_config['connect_str']
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = azure_config['container_name']
        blob_name = azure_config['blob_name']

        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        print("\nUploading to Azure Storage as blob:\n\t" + blob_name)

        # Upload the created file
        with open("data/PressStatesTimelineDataTest.csv", "rb") as data:
            blob_client.upload_blob(data)

    except Exception as ex:
        print('Exception:')
        print(ex)


