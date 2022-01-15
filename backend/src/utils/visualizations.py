import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import norm
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
from moviepy.editor import ImageSequenceClip

from utils.utils import timeit
from utils.keypoints import KEYPOINT_DICT


def plot_y_values(all_keypoints, facing_direction, peak_indices, output_file_path=None):
    ankle_index = KEYPOINT_DICT[f"{facing_direction}_ankle"]
    ankle_y_values = [1 - kp[ankle_index][0] for kp in all_keypoints]
    peak_values = [ankle_y_values[i] for i in peak_indices]
    plt.figure(figsize=(15, 8))
    ax = plt.gca()
    sns.set_style(style="white")
    sns.lineplot(x=list(range(len(all_keypoints))), y=ankle_y_values, ax=ax)
    sns.lineplot(x=peak_indices, y=peak_values, ax=ax)
    plt.xlabel(
        xlabel="Frame",
        fontdict={"family": "serif", "color": "black", "weight": "bold", "size": 24},
    )
    plt.ylabel(
        ylabel="Y-Coordinate",
        fontdict={"family": "serif", "color": "black", "weight": "bold", "size": 24},
    )
    ax.yaxis.set_tick_params(labelcolor="black", labelsize=20)
    ax.xaxis.set_tick_params(labelcolor="black", labelsize=20)
    if output_file_path is not None:
        plt.savefig(output_file_path, transparent=True)
    plt.close()


def plot_angle_values(angles, peak_indices, output_file_path=None):
    angles = [angle[1] for angle in angles]
    peak_angles = [angles[i] for i in peak_indices]
    sns.lineplot(x=list(range(len(angles))), y=angles)
    sns.lineplot(x=peak_indices, y=peak_angles)
    if output_file_path is not None:
        plt.savefig(output_file_path)
    plt.close()


def draw_angle_on_image(
    frame,
    coordinates,
    start_angle,
    knee_angle,
    facing_direction,
    pie_slice_width,
    output_file_path=None,
):
    """Draws the inner-knee angle on the frame
    Args:
        frame: A numpy array with shape [heigh, width, channels]
        coordinates: [hipxy, kneexy, anklexy] list of coordinates
        start_angle: angle between thigh and horizontal bottom of image in degrees
        knee_angle: inner knee angle in degrees
        facing_direction: 'left' or 'right'
        pie_slice_width: width of the drawn pie slice
        output_file_path: path to save the image to
    Returns:
        numpy array of image
    """

    pie_color = "green" if 140 <= knee_angle <= 150 else "red"

    height, width, _ = frame.shape
    height_ratio = height / 720
    pie_slice_width = int(round(pie_slice_width * height_ratio))
    coordinates = [(coord[0] * width, coord[1] * height) for coord in coordinates]

    image = Image.fromarray(np.uint8(frame))
    draw = ImageDraw.Draw(image)
    if facing_direction == "left":
        draw.pieslice(
            [
                (
                    coordinates[1][0] - pie_slice_width,
                    coordinates[1][1] - pie_slice_width,
                ),
                (
                    coordinates[1][0] + pie_slice_width,
                    coordinates[1][1] + pie_slice_width,
                ),
            ],
            start_angle - 90,
            knee_angle - 90 + start_angle,
            pie_color,
        )
    else:
        draw.pieslice(
            [
                (
                    coordinates[1][0] - pie_slice_width,
                    coordinates[1][1] - pie_slice_width,
                ),
                (
                    coordinates[1][0] + pie_slice_width,
                    coordinates[1][1] + pie_slice_width,
                ),
            ],
            -start_angle - 90 - knee_angle,
            -start_angle - 90,
            pie_color,
        )
    if output_file_path is not None:
        image.save(output_file_path)
    return np.array(image)

def draw_plot_of_angle(
    timestamp, timestamps, angles, timestamps_used, angles_used
):
    fig = plt.figure()
    plt.xlim(-1, 1)
    x = [t - timestamp for t in timestamps]
    x_used = [t - timestamp for t in timestamps_used]
    plt.plot(x, angles, color="blue", marker="o")
    plt.plot(
        x_used, angles_used, color="green", marker="o", markersize=10, linewidth=0
    )
    plt.axvline(x=0, color="k", linestyle="--")
    fig.canvas.draw()
    data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    plt.close()
    return data


def plotting_angles(angles_at_peaks, lower_bound, upper_bound, output_file_path):
    """Draws a plot of the peak angles over time
    Args:
        angles_at_peaks: A list of integers that represent inner-knee angles at the peaks
        lower_bound: the smallest angle that is considered acceptable (int)
        upper_bound: the largest angle that is considered acceptable (int)
    Returns:
        a plot that shows the peak angles over time
    """
    peak_indices = range(len(angles_at_peaks))
    lower_bound = [lower_bound] * len(angles_at_peaks)
    upper_bound = [upper_bound] * len(angles_at_peaks)

    df = pd.DataFrame(list(zip(angles_at_peaks)), columns=["vals"])
    average = [float(df["vals"].mean())] * len(angles_at_peaks)
    df = pd.DataFrame(
        (list(zip(angles_at_peaks, upper_bound, lower_bound, average))),
        columns=["peak_angles", "up_bound", "low_bound", "average"],
    )

    cmap = sns.color_palette("rocket", 4)
    sns.set(rc={"figure.figsize": (15, 8)})
    sns.lineplot(data=df, palette=cmap, dashes=[(1, 0), (2, 2), (2, 2), (2, 2)])
    plt.fill_between(
        peak_indices,
        df.low_bound,
        df.peak_angles,
        where=df.peak_angles <= df.low_bound,
        interpolate=True,
    )
    plt.fill_between(
        peak_indices,
        df.up_bound,
        df.peak_angles,
        where=df.peak_angles >= df.up_bound,
        interpolate=True,
    )
    plt.savefig(output_file_path)
    plt.close()


def plot_normal_distribution(
    values, output_file_path, nr_of_bins=None, use_normal=True
):
    """Draws a normal distribution of values
    Args:
        values: A list of values for which we plot the distribution
        output_file_path: the file path to save the plot to
        nr_of_bins: Shows how many bins are used for the distribution (can be 'None' for automatic use)
        use_normal: Boolean that decides if a normal is returned on top of the graph
    Returns:
        a plot that shows the a distribution of peak angles with density
    """

    sns.set(rc={"figure.figsize": (15, 8)})
    df = pd.DataFrame(list(zip(values)), columns=["vals"])
    if use_normal:
        if nr_of_bins is not None:
            sns.distplot(df, bins=nr_of_bins, rug=True, fit=norm)
        else:
            sns.distplot(df, rug=True, fit=norm)
    else:
        if nr_of_bins is not None:
            sns.distplot(df, bins=nr_of_bins, rug=True)
        else:
            sns.distplot(df, rug=True)

    plt.savefig(output_file_path)
    plt.close()


@timeit
def write_video_to_files(images, fps, output_file_path):
    clip = ImageSequenceClip(images, fps)
    clip.write_videofile(output_file_path, audio=False, verbose=False, logger=None)
