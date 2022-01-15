"""
This file implements the init and run functions needed to create a REST API for a deployed model on the Azure ML service.
The init function loads and saves a referecence to the model from tensorflow hub
The run function performs inference on the provided video, by:
- Downloading the video from blob storage
- Preprocessing the video
- Passing the preprocessed video through the MoveNet model
- Postprocessing the keypoints returned to calculate a recommendation
- Creating visualizations of the results
- Uploading the results to blob storage
"""

import time
import json
import os
import logging
import shutil
import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import VideoFileClip, ImageSequenceClip, clips_array

from utils.azure import (
    delete_blob_from_storage_account,
    download_video_from_storageaccount,
    upload_results_to_storageaccount,
)
from utils.preprocessing import reduce_video_quality, load_tensors_from_clip
from utils.model import load_model_from_tfhub, get_keypoints_from_video
from utils.postprocessing import (
    find_camera_facing_side,
    get_front_leg_keypoint_indices,
    get_lowest_pedal_frames,
    get_hipkneeankle_coords,
    calc_knee_angle,
    filter_bad_angles,
    make_recommendation,
)
from utils.visualizations import (
    draw_angle_on_image,
    draw_plot_of_angles,
    plot_angle_values,
    plot_normal_distribution,
    plot_y_values,
    draw_plot_of_angles
)
from utils.utils import (timeit)


def pre_process_video(file_path):
    clip = reduce_video_quality(file_path, max_pixels=256, max_fps=15, max_duration=10)
    tensors = load_tensors_from_clip(clip)
    return clip, tensors

@timeit
def post_process_video(all_keypoints, ideal_angle=145):
    facing_direction = find_camera_facing_side(all_keypoints[0])
    hipkneeankleindices = get_front_leg_keypoint_indices(facing_direction)
    all_angles = [
        calc_knee_angle(get_hipkneeankle_coords(kp, hipkneeankleindices))
        for kp in all_keypoints
    ]

    lowest_pedal_point_indices = get_lowest_pedal_frames(
        all_keypoints, hipkneeankleindices
    )
    angles_at_lowest_pedal_points = [
        all_angles[i][1] for i in lowest_pedal_point_indices
    ]
    angles_at_lowest_pedal_points, lowest_pedal_point_indices = filter_bad_angles(
        angles_at_lowest_pedal_points, lowest_pedal_point_indices
    )
    angle_at_lowest_pedal_points_avg, angle_at_lowest_pedal_points_std = np.mean(
        angles_at_lowest_pedal_points
    ), np.std(angles_at_lowest_pedal_points)
    recommendation = make_recommendation(
        angle_at_lowest_pedal_points_avg, ideal_angle=ideal_angle
    )
    return (
        facing_direction,
        hipkneeankleindices,
        all_angles,
        lowest_pedal_point_indices,
        angles_at_lowest_pedal_points,
        angle_at_lowest_pedal_points_avg,
        angle_at_lowest_pedal_points_std,
        recommendation,
    )


def create_visualizations(
    file_name,
    tensors,
    all_keypoints,
    hipkneeankleindices,
    facing_direction,
    all_angles,
    lowest_pedal_point_indices,
    angles_at_lowest_pedal_points,
    results,
):
    # ankle y values
    y_value_plot_file_path = f"{file_name}_yvalues.png"
    plot_y_values(
        all_keypoints,
        facing_direction,
        lowest_pedal_point_indices,
        output_file_path=y_value_plot_file_path,
    )
    results["y_value_plot_file_path"] = y_value_plot_file_path
    # angle values
    angle_value_plot_file_path = f"{file_name}_anglevalues.png"
    plot_angle_values(
        all_angles,
        lowest_pedal_point_indices,
        output_file_path=angle_value_plot_file_path,
    )
    results["angle_value_plot_file_path"] = angle_value_plot_file_path

    # plot normal distribution of angles
    output_normal_graph_file_path = f"{file_name}_normalgraph.png"
    plot_normal_distribution(
        angles_at_lowest_pedal_points, output_normal_graph_file_path
    )
    results["output_normal_graph_file_path"] = output_normal_graph_file_path

    # plot frame with angle on most average angle
    angle_image_file_path = f"{file_name}.png"
    frame_idx = lowest_pedal_point_indices[0]
    draw_angle_on_image(
        tensors[frame_idx],
        get_hipkneeankle_coords(all_keypoints[frame_idx], hipkneeankleindices),
        all_angles[frame_idx][0],
        all_angles[frame_idx][1],
        facing_direction,
        pie_slice_width=100,
        output_file_path=angle_image_file_path,
    )
    results["angle_image_file_path"] = angle_image_file_path
    blobs_to_upload = [
        angle_image_file_path,
        output_normal_graph_file_path,
        y_value_plot_file_path,
        angle_value_plot_file_path,
    ]
    return results, blobs_to_upload

def create_video_visualization(
    file_name, 
    tensors, 
    all_keypoints, 
    hipkneeankleindices, 
    facing_direction, 
    all_angles, 
    lowest_pedal_point_indices, 
    results, 
    clip
):
    # Angle video
    angle_video_file_path = f"{file_name}_anglevideo.mp4"
    # right side of video
    frames_with_angle = [
        np.uint8(tensors[i])
        if i not in lowest_pedal_point_indices
        else draw_angle_on_image(
            tensors[i],
            get_hipkneeankle_coords(all_keypoints[i], hipkneeankleindices),
            all_angles[i][0],
            all_angles[i][1],
            facing_direction,
            pie_slice_width=100,
        )
        for i in range(len(all_keypoints))
    ]
    #left side of video
    frames_plots = draw_plot_of_angles(results, clip)

    #combining videos
    clip_right = ImageSequenceClip(frames_with_angle, fps=clip.fps)
    clip_left = ImageSequenceClip(frames_plots, fps=clip.fps)
    clip_array = clips_array([[clip_left, clip_right]])
    clip_array.write_videofile(angle_video_file_path)
    results["angle_video_file_path"] = angle_video_file_path
    blobs_to_upload= [angle_video_file_path]
    return results, blobs_to_upload


def upload_results(file_name, results, blobs_to_upload):
    if results is not None:
        json_file_path = f"{file_name}.json"
        with open(json_file_path, "w") as file:
            json.dump(results, file)
        blobs_to_upload.append(json_file_path)

    upload_results_to_storageaccount(
        os.getenv("AZURE_STORAGE_CONNECTION_ACCOUNT"),
        container="results",
        blobs=blobs_to_upload,
    )


def cleanup(file_path, blobs_to_upload):
    os.remove(file_path)
    for blob_name in blobs_to_upload:
        os.remove(blob_name)
    delete_blob_from_storage_account(
        os.getenv("AZURE_STORAGE_CONNECTION_ACCOUNT"),
        container="videos",
        file_path=file_path,
    )


def init():
    global model, input_size
    logging.getLogger("azure").setLevel(logging.ERROR)
    model, input_size = load_model_from_tfhub(model_name="movenet_thunder")


def run(Inputs):
    logging.info(f"STARTED INFERENCE ON {Inputs}")
    start = time.time()
    data = json.loads(Inputs)
    file_path = data["file_name"]

    download_video_from_storageaccount(
        account_name=os.getenv("AZURE_STORAGE_CONNECTION_ACCOUNT"),
        container="videos",
        file_path=file_path,
    )
    file_name, extension = file_path.split(".")

    # Preprocess video
    clip, tensors = pre_process_video(file_path)

    # Inference on model
    all_keypoints = get_keypoints_from_video(tensors, model, input_size)

    # Post process keypoints
    (
        facing_direction,
        hipkneeankleindices,
        all_angles,
        lowest_pedal_point_indices,
        angles_at_lowest_pedal_points,
        angle_at_lowest_pedal_points_avg,
        angle_at_lowest_pedal_points_std,
        recommendation,
    ) = post_process_video(all_keypoints)

    # Save Results
    sec_per_frame = 1 / clip.fps
    results = {
        "recommendation": recommendation,
        "angle": angle_at_lowest_pedal_points_avg,
        "std": angle_at_lowest_pedal_points_std,
        "ideal_angle": 145,
        "difference": angle_at_lowest_pedal_points_avg - 145,
        "timestamped_angles": [
            (i * sec_per_frame, all_angles[i][1]) for i in range(len(all_angles))
        ],
        "used_timestamped_angles": [
            (i * sec_per_frame, all_angles[i][1]) for i in lowest_pedal_point_indices
        ],
    }
    # VISUALIZATIONS 1
    results, blobs_to_upload = create_visualizations(
        file_name,
        tensors,
        all_keypoints,
        hipkneeankleindices,
        facing_direction,
        all_angles,
        lowest_pedal_point_indices,
        angles_at_lowest_pedal_points,
        results,
    )
    upload_results(file_name, results, blobs_to_upload)

    # VISUALIZATIONS 2
    results, blobs_to_upload = create_video_visualization(
        file_name, 
        tensors, 
        all_keypoints, 
        hipkneeankleindices, 
        facing_direction, 
        all_angles, 
        lowest_pedal_point_indices, 
        results, 
        clip
    )
    upload_results(file_name, results=None, blobs_to_upload)

    # Cleanup
    cleanup(file_path, blobs_to_upload)
    return f"Finished inference on {file_path} in {time.time()-start:.2f} sec"