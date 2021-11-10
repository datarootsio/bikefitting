import unittest
import os
import sys

# add src dir to sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from utils.postprocessing import calc_knee_angle
from utils.postprocessing import find_camera_facing_side
from utils.postprocessing import filter_bad_angles
from utils.postprocessing import make_recommendation


class TestPostProcessing(unittest.TestCase):
    def test_calc_knee_angle(self):
        start_angle, knee_angle = calc_knee_angle([[100, 100], [50, 150], [100, 200]])
        self.assertEqual(round(start_angle), 45)
        self.assertEqual(round(knee_angle), 90)
        start_angle, knee_angle = calc_knee_angle([[100, 100], [150, 150], [100, 200]])
        self.assertEqual(round(start_angle), 45)
        self.assertEqual(round(knee_angle), 90)
        start_angle, knee_angle = calc_knee_angle([[100, 100], [150, 100], [150, 200]])
        self.assertEqual(round(start_angle), 90)
        self.assertEqual(round(knee_angle), 90)
        start_angle, knee_angle = calc_knee_angle([[100, 100], [50, 100], [50, 200]])
        self.assertEqual(round(start_angle), 90)
        self.assertEqual(round(knee_angle), 90)

    def test_find_camera_facing_side(self):
        keypoints1 = [
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
        keypoints2 = [
            [0, 5],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [11, 3],
            [],
            [],
            [],
            [],
        ]
        keypoints3 = [
            [0, 9],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [11, 5],
            [],
            [],
            [],
            [],
        ]
        keypoints4 = [
            [0, 9],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [11, 12],
            [],
            [],
            [],
            [],
        ]
        self.assertEqual(find_camera_facing_side(keypoints1), "left")
        self.assertEqual(find_camera_facing_side(keypoints2), "right")
        self.assertEqual(find_camera_facing_side(keypoints3), "right")
        self.assertEqual(find_camera_facing_side(keypoints4), "left")

    def test_filter_bad_angles(self):
        input_angles = [50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180]
        input_indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        angles, indices = filter_bad_angles(input_angles, input_indices)
        for angle in angles:
            self.assertGreater(angle, 130)
            self.assertLess(angle, 170)

    def test_make_recommendation(self):
        self.assertEqual(
            make_recommendation(inner_knee_angle=143, ideal_angle=145, buffer=5), "NOOP"
        )
        self.assertEqual(
            make_recommendation(inner_knee_angle=151, ideal_angle=145, buffer=5), "DOWN"
        )
        self.assertEqual(
            make_recommendation(inner_knee_angle=138, ideal_angle=145, buffer=5), "UP"
        )
        self.assertEqual(
            make_recommendation(inner_knee_angle=143, ideal_angle=145, buffer=1), "UP"
        )
        self.assertEqual(
            make_recommendation(inner_knee_angle=150, ideal_angle=145, buffer=1), "DOWN"
        )
        self.assertEqual(
            make_recommendation(inner_knee_angle=145, ideal_angle=145, buffer=1), "NOOP"
        )
        self.assertEqual(
            make_recommendation(inner_knee_angle=168, ideal_angle=170, buffer=5), "NOOP"
        )
        self.assertEqual(
            make_recommendation(inner_knee_angle=0, ideal_angle=170, buffer=5), "UP"
        )
