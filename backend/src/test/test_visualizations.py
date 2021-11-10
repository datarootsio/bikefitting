import unittest
import tensorflow as tf
import numpy as np
from moviepy.editor import VideoFileClip
import os
import sys

# add src dir to sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from utils.visualizations import draw_angle_on_image


class TestVisualizations(unittest.TestCase):
    def test_draw_angle_on_image(self):
        clip = VideoFileClip("backend/src/test/test_video.mp4", audio=False)
        video_tensor = tf.convert_to_tensor(
            np.array(list(clip.iter_frames())), dtype=tf.uint8
        )
        output_array = draw_angle_on_image(
            video_tensor[1], [[100, 100], [150, 100], [150, 150]], 90, 90, "right", 100
        )
        a = np.array([1])
        self.assertEqual(type(output_array), type(a))
