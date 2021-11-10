import unittest
import os
import sys

# add src dir to sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from utils.preprocessing import reduce_video_quality


class TestPreProcessing(unittest.TestCase):
    def test_reduce_video_quality(self):
        size = 100
        fps = 15
        duration = 10
        result = reduce_video_quality(
            "./backend/src/test/test_video.mp4", size, fps, duration
        )
        self.assertLessEqual(result.fps, fps)
        self.assertEqual(result.size[0], (size * 1.77))
        self.assertEqual(result.size[1], size)
        self.assertLessEqual(result.duration, duration)
