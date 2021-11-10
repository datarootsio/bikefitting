"""""" """""" """""" """""
PREPROCESSING FUNCTIONS
""" """""" """""" """""" ""
import logging
import numpy as np
import tensorflow as tf
from moviepy.editor import VideoFileClip
from utils.utils import timeit


@timeit
def reduce_video_quality(video_path, max_pixels, max_fps, max_duration):
    clip = VideoFileClip(video_path, audio=False)
    # Reduce fps
    max_fps = min(clip.fps, max_fps)
    clip = clip.set_fps(max_fps)
    # Reduce resolution
    max_pixels = min(min(clip.h, clip.w), max_pixels)
    clip = (
        clip.resize(height=max_pixels)
        if clip.h < clip.w
        else clip.resize(width=max_pixels)
    )
    # Reduce duration
    mid_point = clip.duration / 2
    lower_point = mid_point - max_duration / 2
    upper_point = mid_point + max_duration / 2
    clip = clip.subclip(lower_point, upper_point)
    print(
        f"Clip with fps: {clip.fps} - width: {clip.w} - height: {clip.h} - duration: {clip.duration}"
    )
    return clip


@timeit
def load_tensors_from_clip(videofileclip):
    # convert to uint8 array of frames
    video = tf.convert_to_tensor(
        np.array(list(videofileclip.iter_frames())), dtype=tf.uint8
    )
    logging.info("Converted video to tf.Tensor")
    return video
