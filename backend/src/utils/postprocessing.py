"""""" """""" """""" """""" """
 POSTPROCESSING FUNCTIONS
""" """""" """""" """""" """"""
import math
import numpy as np
from scipy.signal import find_peaks
from utils.keypoints import KEYPOINT_DICT


def find_camera_facing_side(keypoints):
    """Returns whether the cyclist is facing the camera with his left or right side
    Args:
        nosex: float representing the x coordinate of the nose (x=0 if point is on the left border of the image)
        hipx: float representing the x coordinate of the hip (either left or right)
    Returns:
        'left' if the left leg is facing the camera, 'right' otherwise
    """
    hipx = keypoints[KEYPOINT_DICT["left_hip"]][
        1
    ]  # we take left hip, but it doesn't really matter
    nosex = keypoints[KEYPOINT_DICT["nose"]][1]
    return "left" if nosex < hipx else "right"


def get_front_leg_keypoint_indices(facing_dir):
    hip_index = KEYPOINT_DICT[f"{facing_dir}_hip"]
    knee_index = KEYPOINT_DICT[f"{facing_dir}_knee"]
    ankle_index = KEYPOINT_DICT[f"{facing_dir}_ankle"]
    return hip_index, knee_index, ankle_index


def get_lowest_pedal_frames(all_keypoints, hipkneeankleindices):
    ankle_index = hipkneeankleindices[2]
    ankle_y_values = []
    for frame_idx in range(len(all_keypoints)):
        ankle_y_values.append(all_keypoints[frame_idx][ankle_index][0])
    # the distance variable lets you to easily pick only the highest peak values and ignore local jitters in a pedal rotation
    peak_indices = find_peaks(ankle_y_values, distance=10)[0]
    return peak_indices


def get_hipkneeankle_coords(keypoint, indices):
    [hip_y, hip_x] = keypoint[indices[0]][0:-1]
    [knee_y, knee_x] = keypoint[indices[1]][0:-1]
    [ankle_y, ankle_x] = keypoint[indices[2]][0:-1]
    return [(hip_x, hip_y), (knee_x, knee_y), (ankle_x, ankle_y)]


def calc_knee_angle(hipkneeankle_coords):
    """Calculates the inner knee-angle.
    Args:
        hipxy: A tuple of floats containing the coordinates of the hip
        kneexy: A tuple of floats containing the coordinates of the knee
        anklexy: A tuple of floats containing the coordinates of the ankle
    Returns:
        The angle between the upper thigh and horizontal bottom of the image.
        The inner-knee angle in degrees.
    """
    line1 = math.sqrt(
        math.pow(hipkneeankle_coords[1][0] - hipkneeankle_coords[0][0], 2)
        + math.pow(hipkneeankle_coords[1][1] - hipkneeankle_coords[0][1], 2)
    )
    line2 = math.sqrt(
        math.pow(hipkneeankle_coords[1][0] - hipkneeankle_coords[2][0], 2)
        + math.pow(hipkneeankle_coords[1][1] - hipkneeankle_coords[2][1], 2)
    )
    line3 = math.sqrt(
        math.pow(hipkneeankle_coords[0][0] - hipkneeankle_coords[2][0], 2)
        + math.pow(hipkneeankle_coords[0][1] - hipkneeankle_coords[2][1], 2)
    )

    vertical_line = math.sqrt(
        math.pow(hipkneeankle_coords[1][0] - hipkneeankle_coords[1][0], 2)
        + math.pow(hipkneeankle_coords[1][1] - (hipkneeankle_coords[1][1] - 100), 2)
    )
    vertical_cross_line = math.sqrt(
        math.pow(hipkneeankle_coords[1][0] - hipkneeankle_coords[0][0], 2)
        + math.pow((hipkneeankle_coords[1][1] - 100) - hipkneeankle_coords[0][1], 2)
    )

    start_angle = math.degrees(
        math.acos(
            (
                (
                    math.pow(line1, 2)
                    + math.pow(vertical_line, 2)
                    - math.pow(vertical_cross_line, 2)
                )
                / (2 * line1 * vertical_line)
            )
        )
    )
    knee_angle = math.degrees(
        math.acos(
            (
                (math.pow(line1, 2) + math.pow(line2, 2) - math.pow(line3, 2))
                / (2 * line1 * line2)
            )
        )
    )
    return start_angle, knee_angle


def filter_bad_angles(angles, indices, m=2.0):
    """Filters out outliers from the passed list.
    Args:
        angles: list of angles to filter
        indices: original indices in the video to which the angles correspond
        m: the maximum distance
    Returns:
        list of angles that were kept
        list of indices that were kept
    """
    indices = np.array(indices)
    angles = np.array(angles)
    mask = (130 < angles) & (angles < 170)
    angles = angles[mask]
    indices = indices[mask]
    # calc dist to median (median is more robust to outliers than mean)
    dist = np.abs(angles - np.median(angles))
    # get median of distances
    mdev = np.median(dist)
    # scale the distances based on median of distances
    s = dist / mdev if mdev else 0.0
    mask = s < m
    return angles[mask], indices[mask]


def make_recommendation(inner_knee_angle, ideal_angle=145, buffer=5):
    """Returns a recommendation based on the difference from the ideal angle
    Args:
        inner_knee_angle: actual angle of the user
        ideal_angle: target angle
        buffer: accepted range above and below ideal_angle
    Returns:
        str: 'UP', 'DOWN', 'NOOP'
    """
    if inner_knee_angle < ideal_angle - buffer:
        return "UP"
    elif inner_knee_angle > ideal_angle + buffer:
        return "DOWN"
    return "NOOP"
