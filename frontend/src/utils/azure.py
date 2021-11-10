import os
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()


def _get_blobserviceclient():
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(
        account_url=f"https://{os.getenv('AZURE_STORAGE_CONNECTION_ACCOUNT')}.blob.core.windows.net",
        credential=credential,
    )
    return blob_service_client


def download_results(container, blobs):
    """download the results to session
    Args:
        container: container to download from
        blobs: list of blob names
        results: dict containing entries for blobs
    """
    blob_service_client = _get_blobserviceclient()
    blob_dict = dict()
    for blob_file_name in blobs:
        blob_client = blob_service_client.get_blob_client(
            container=container, blob=blob_file_name
        )
        blob_dict[blob_file_name] = blob_client.download_blob().readall()
    return blob_dict


def delete_results(container, blobs):
    """delete the results on Azure
    Args:
        container: container where blobs are located
        blobs: list of blob names
    """
    blob_service_client = _get_blobserviceclient()
    for blob_file_name in blobs:
        blob_client = blob_service_client.get_blob_client(
            container=container, blob=blob_file_name
        )
        blob_client.delete_blob(delete_snapshots="include")


def upload_file(uploaded_file):
    blob_service_client = _get_blobserviceclient()
    blob_client_up = blob_service_client.get_blob_client(
        container="videos", blob=uploaded_file.name
    )
    blob_client_up.upload_blob(uploaded_file)
