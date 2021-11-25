import re
import time
import uuid
import json
import streamlit as st
from zipfile import ZipFile
import os
import sys

# add src dir to sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from utils.azure import delete_results, download_results, upload_file
from utils.datahandling import get_file_extension, interpret_model_recommendation
from utils.visualizations import build_plot_video
from utils.utils import get_string_from_file, get_image_path


def page_config():
    st.set_page_config(
        page_title="Bike Posture Analysis Tool - Dataroots",
        page_icon=get_image_path("dataroots_logo.png"),
        layout="centered",
        initial_sidebar_state="expanded",
        menu_items={"About": "# This is an *extremely* cool app!"},
    )


def title():
    st.image(get_image_path("dataroots_title.png"))
    st.title("Bike Posture Analysis Tool")


def setup_explanation():
    st.markdown(get_string_from_file("upload_instructions.txt"))
    with st.expander("Click here to see our example set-up"):
        st.markdown(get_string_from_file("setup.txt"))
        st.image(get_image_path("setup_picture.jpg"))

    st.markdown(get_string_from_file("only_on_bike_footage.txt"))


def upload_file_to_azure(uploaded_file):
    extension = get_file_extension(uploaded_file)
    unique_id = uuid.uuid1()
    original_name = str.split(uploaded_file.name, ".")[0]
    uploaded_file.name = f"{unique_id}.{extension}"
    upload_file(uploaded_file)
    return original_name, unique_id


def download_results_from_azure(blobs):
    with st.spinner("""I'm telling the model to do things. It's out of my hands!"""):
        while True:
            try:
                results = download_results(container="results", blobs=blobs)
                break
            except Exception:
                time.sleep(1)

    st.balloons()
    st.success("The model is ready!")
    # delete results on azure
    delete_results(container="results", blobs=blobs)
    return results


def results_recommendation(results, unique_id):
    st.header("Results")
    blob_data_json = json.loads(results[f"{unique_id}.json"])
    recommendation = blob_data_json["recommendation"]
    recommendation, pointer = interpret_model_recommendation(recommendation)

    rec_string = f"""The knee-angle at the lowest point was **{round(blob_data_json['angle'])}**.
    A comfortable knee-angle is {blob_data_json['ideal_angle']}°,
    a {round(blob_data_json['difference'])} degree difference.
    We recommend you **{recommendation}** the height of your saddle."""

    st.markdown(rec_string)
    col1, col2 = st.columns(2)
    col1.metric("Knee-Angle", f"{round(blob_data_json['angle'])}°")
    col2.metric("Recommendation", recommendation, pointer)
    return recommendation, blob_data_json


def results_methodology(results, unique_id):
    with st.expander("Click here to read about the methodology"):
        st.markdown(get_string_from_file("methodology.txt"))
        st.image(results[f"{unique_id}_normalgraph.png"])


def results_videoplot(results, blob_data_json, unique_id):
    with st.spinner("A video is being processed"):
        video_name = build_plot_video(results, unique_id, blob_data_json)
        st.video(video_name)
        os.remove(video_name)


def download_zip(results, original_name, unique_id):
    st.header("Download")

    st.markdown(
        """
    Your results are now ready to be downloaded.
    """
    )
    result_zip_name = f"results_{original_name}.zip"
    with ZipFile(result_zip_name, "w") as zipfile:
        for file_name, file_data in results.items():
            file_name = re.sub(str(unique_id), original_name, file_name)
            with open(file_name, "wb") as file:
                file.write(file_data)
            zipfile.write(file_name)
            os.remove(file_name)

    with open(result_zip_name, "rb") as fp:
        st.download_button(label="Download results", data=fp, file_name=result_zip_name)
    os.remove(result_zip_name)


def follow_up(recommendation):
    if recommendation != "don't change":
        st.header("Follow up")
        st.markdown(get_string_from_file("followup_change.txt"))
    if recommendation == "don't change":
        st.header("Follow Up")
        st.markdown(get_string_from_file("followup_nochange.txt"))
