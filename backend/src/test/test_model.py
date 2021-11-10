import unittest
import tensorflow as tf
import numpy as np
from moviepy.editor import VideoFileClip
import os
import sys

# add src dir to sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from utils.model import load_model_from_tfhub
from utils.model import get_keypoints_from_video


class TestModel(unittest.TestCase):
    def test_load_model_from_tf_hub(self):
        _, size1 = load_model_from_tfhub(model_name="movenet_thunder")
        _, size2 = load_model_from_tfhub(model_name="movenet_lightning")
        self.assertEqual(size1, 256)
        self.assertEqual(size2, 192)

    def test_get_keypoints_from_video(self):
        model, input_size = load_model_from_tfhub(model_name="movenet_thunder")
        clip = VideoFileClip("backend/src/test/test_video.mp4", audio=False)
        video_tensor = tf.convert_to_tensor(
            np.array(list(clip.iter_frames())), dtype=tf.uint8
        )
        keypoints = get_keypoints_from_video(video_tensor, model, input_size)
        keypoints = np.array(keypoints)
        n_frames = 225
        n_keypoints = 17
        n_coordinates = 3
        self.assertEqual(keypoints.shape, (n_frames, n_keypoints, n_coordinates))
        pass
