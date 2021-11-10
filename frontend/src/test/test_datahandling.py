import unittest
import io
import os
import sys

# add src dir to sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from utils.datahandling import interpret_model_recommendation, get_file_extension


class TestDatahandling(unittest.TestCase):
    def test_interpret_model_recommendation(self):
        self.assertNotEqual(interpret_model_recommendation("UP"), "lower")
        self.assertNotEqual(interpret_model_recommendation("UP"), "don't change")
        self.assertNotEqual(interpret_model_recommendation("DOWN"), "raise")
        self.assertNotEqual(interpret_model_recommendation("DOWN"), "don't change")
        self.assertNotEqual(interpret_model_recommendation("NOOP"), "raise")
        self.assertNotEqual(interpret_model_recommendation("NOOP"), "lower")

    def test_get_file_extension(self):
        file_to_upload = io.BytesIO(b"some data")
        file_to_upload.type = "video/webm"
        self.assertEqual(get_file_extension(file_to_upload), "webm")
        file_to_upload.type = "video/mp4"
        self.assertEqual(get_file_extension(file_to_upload), "mp4")
        file_to_upload.type = "video/mov"
        self.assertEqual(get_file_extension(file_to_upload), "mov")
