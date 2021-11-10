import unittest
import os
import sys

# add src dir to sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from utils.azure import (
    _get_blobserviceclient,
    download_results,
    upload_file,
    delete_results,
)
import io


class TestAzure(unittest.TestCase):
    def test_get_blobserviceclient(self):
        # This test requires the following env variables to be set
        # AZURE_STORAGE_CONNECTION_ACCOUNT
        result = _get_blobserviceclient()
        self.assertIsNotNone(result)

    def test_upload_file(self):
        file_to_upload = io.BytesIO(b"some data")
        file_to_upload.name = "test_data.txt"
        upload_file(file_to_upload)

        blobs = ["test_data.txt"]
        container = "videos"
        result = download_results(container, blobs)
        self.assertIsNotNone(result)

        blobs = ["test_data.txt"]
        container = "videos"
        delete_results(container, blobs)
