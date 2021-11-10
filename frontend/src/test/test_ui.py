import unittest
import os
import sys

# add src dir to sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from utils.ui import (
    page_config,
    title,
    setup_explanation,
    upload_file_to_azure,
    delete_results,
)
from streamlit.uploaded_file_manager import UploadedFile, UploadedFileRec
import uuid


class TestUi(unittest.TestCase):
    def test_page_setup(self):
        page_config()
        title()
        setup_explanation()

    def test_upload_file_to_azure(self):
        file_to_upload = UploadedFile(
            record=UploadedFileRec(
                1, name="test_video.webm", type="video/webm", data=b"some data"
            )
        )
        original_name, unique_id = upload_file_to_azure(file_to_upload)
        self.assertEqual(original_name, "test_video")
        self.assertEqual(type(unique_id), type(uuid.uuid1()))

        delete_results(container="videos", blobs=[f"{unique_id}.webm"])
