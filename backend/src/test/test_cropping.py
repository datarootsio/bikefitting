import os
import sys

# add src dir to sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
import unittest
from utils.cropping import determine_crop_region
import numpy as np


class TestCropping(unittest.TestCase):
    def test_determine_crop_region(self):
        image_height = 444
        image_width = 250
        keypoints = [
            [0.21835053, 0.430152, 0.70083785],
            [0.19670622, 0.42337525, 0.7437103],
            [0.20218945, 0.4227556, 0.65788436],
            [0.15137187, 0.44474348, 0.6786951],
            [0.15752277, 0.4407963, 0.6794007],
            [0.17660065, 0.4998227, 0.686523],
            [0.19287342, 0.48497474, 0.64179],
            [0.3007346, 0.42500377, 0.76953834],
            [0.30853492, 0.42676863, 0.50268894],
            [0.40107608, 0.3510163, 0.75954545],
            [0.39778885, 0.36066812, 0.4420318],
            [0.37044775, 0.619631, 0.82676536],
            [0.3628245, 0.5775077, 0.86443317],
            [0.54847145, 0.5104004, 0.819147],
            [0.44436848, 0.46940348, 0.56176305],
            [0.7846267, 0.5127145, 0.8271608],
            [0.5667855, 0.53535676, 0.4370708],
        ]
        keypoints = np.array(keypoints)
        self.assertEqual(
            determine_crop_region(keypoints, image_height, image_width),
            {
                "height": 1.0,
                "width": 1.776,
                "x_max": 1.388,
                "x_min": -0.388,
                "y_max": 1.0,
                "y_min": 0.0,
            },
        )
