#
# def func_azure_uploader_2(blob_name):
#     try:
#         connect_str = azure_config['connect_str']
#         blob_service_client = BlobServiceClient.from_connection_string(connect_str)
#         container_name = azure_config['container_name']
#
#         # Upload the created file
#         blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
#         with open(f"S:\\_db_\\V12App\\data\\{blob_name}", "rb") as data:
#             blob_client.upload_blob(data)
#     except Exception as ex:
#         print('Exception: func_azure_uploader_2 !!!!! Failed')
#         print(ex)
