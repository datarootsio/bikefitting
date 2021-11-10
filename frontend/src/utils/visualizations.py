import os
import shutil
import matplotlib.pyplot as plt
from moviepy.editor import VideoFileClip, ImageSequenceClip, clips_array


def build_plot_video(results, unique_id, json_data_dict):
    """Builds and writes a combined video of the plot of the knee angle and the angle video
    Args:
        results: dictionary of the downloaded files {'file_name': file}
        unique_id: the uuid that was given to the video
        json_data_dict: dictionary of the results returned by the model
    Return:
        None: it saves the results to a local file called final.mp4
    """
    temp_video = f"temp_video_{unique_id}.webm"
    with open(temp_video, "wb") as wfile:
        wfile.write(results[f"{unique_id}_anglevideo.webm"])

    temp_dir = f"temp_images_{unique_id}"
    if not os.path.exists(f"{temp_dir}/"):
        os.makedirs(temp_dir)

    timestamps, angles = zip(*json_data_dict["timestamped_angles"])
    timestamps_used, angles_used = zip(*json_data_dict["used_timestamped_angles"])

    for timestamp in timestamps:
        plt.figure()
        plt.xlim(-1, 1)
        x = [t - timestamp for t in timestamps]
        x_used = [t - timestamp for t in timestamps_used]
        plt.plot(x, angles, color="blue", marker="o")
        plt.plot(
            x_used, angles_used, color="green", marker="o", markersize=10, linewidth=0
        )
        plt.axvline(x=0, color="k", linestyle="--")
        image_name = f"{timestamp:.3f}.png"
        plt.savefig(os.path.join(temp_dir, image_name))
        plt.close()

    clip_angle_video = VideoFileClip(temp_video, audio=False)
    clip_plots = ImageSequenceClip(temp_dir, fps=15, load_images=True).resize(
        height=clip_angle_video.h
    )
    clip_array = clips_array([[clip_plots, clip_angle_video]])
    final_name = f"final_{unique_id}.mp4"
    clip_array.write_videofile(final_name)

    os.remove(temp_video)
    shutil.rmtree(temp_dir)
    return final_name
