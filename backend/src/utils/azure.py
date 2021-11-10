"""""" """""" """""" """""
AZURE RELATED FUNCTIONS
""" """""" """""" """""" ""
import logging
from utils.utils import timeit
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


def _get_blob_service_client(account_name):
    credential = DefaultAzureCredential(exclude_shared_token_cache_credential=True)
    return BlobServiceClient(
        account_url=f"https://{account_name}.blob.core.windows.net",
        credential=credential,
    )


@timeit
def download_video_from_storageaccount(account_name, container, file_path):
    blob_service_client = _get_blob_service_client(account_name)
    blob_client = blob_service_client.get_blob_client(
        container=container, blob=file_path
    )

    with open(file_path, "wb") as local_file:
        blob_data = blob_client.download_blob()
        blob_data.readinto(local_file)
        logging.info(f"Downloaded {file_path} to local disk")


@timeit
def upload_results_to_storageaccount(account_name, container, blobs):
    """Uploads the results to a blob storage. Overwrites if the blob already exists
    Args:
        account_name: account_name of the storage account
        account_key: key of the storage account
        container: container to upload in
        blobs: dict containing entries for each file to be uploaded {'file_name'}
    """
    blob_service_client = _get_blob_service_client(account_name)
    for blob_file_name in blobs:
        blob_client = blob_service_client.get_blob_client(
            container=container, blob=blob_file_name
        )
        with open(blob_file_name, "rb") as blob:
            blob_client.upload_blob(blob, overwrite=True)
        logging.info(f"Uploaded {blob_file_name} to blob storage")


@timeit
def delete_blob_from_storage_account(account_name, container, file_path):
    blob_service_client = _get_blob_service_client(account_name)
    blob_client = blob_service_client.get_blob_client(
        container=container, blob=file_path
    )
    blob_client.delete_blob(delete_snapshots="include")
    logging.info(f"Deleted {file_path} from blob storage")
