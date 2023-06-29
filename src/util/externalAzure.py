from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

try:
    blob_service_client = BlobServiceClient.from_connection_string(
        "DefaultEndpointsProtocol=https;AccountName=v12daily;AccountKey=2tBxBHZwM5WNyzPAyozRtsircGCFBAMN2S3TfZGFN923bIlkWAjdn5scM5vV5TkYPFKvukfD/cL5+AStMluGag==;EndpointSuffix=core.windows.net")
    blob_client = blob_service_client.get_blob_client("gcsteamcont", "danindeplc-ios-data-history.csv")

    with open("data\\danindeplc-ios-data-history.csv", "rb") as data:
        blob_client.upload_blob(data)

except Exception as ex:
    print('Exception:')
    print(ex)

