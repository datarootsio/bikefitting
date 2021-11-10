import unittest
import os
import sys

# add src dir to sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from utils.utils import get_string_from_file


class TestUtils(unittest.TestCase):
    def test_get_string_from_file(self):
        result = get_string_from_file("setup.txt")
        self.assertEqual(type(result), type("test"))
