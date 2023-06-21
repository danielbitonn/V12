# from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
#
# def FazureUploading():
#     try:
#         connect_str = "DefaultEndpointsProtocol=https;AccountName=v12daily;AccountKey=2tBxBHZwM5WNyzPAyozRtsircGCFBAMN2S3TfZGFN923bIlkWAjdn5scM5vV5TkYPFKvukfD/cL5+AStMluGag==;EndpointSuffix=core.windows.net"
#         blob_service_client = BlobServiceClient.from_connection_string(connect_str)
#         container_name = "gcsteamcont"
#         blob_name = "test_to_gcsteamcont.csv"
#
#
#         blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
#
#         print("\nUploading to Azure Storage as blob:\n\t" + blob_name)
#
#         # Upload the created file
#         with open("data/PressStatesTimelineDataTest.csv", "rb") as data:
#             blob_client.upload_blob(data)
#
#     except Exception as ex:
#         print('Exception:')
#         print(ex)
#