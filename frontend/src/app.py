"""
This file represents the website interface used to:
- upload videos for the backend to analyze
- and display the results to the user.
This website is built with streamlit.
"""
import logging
from utils import ui
import streamlit as st

logging.getLogger("azure").setLevel(logging.ERROR)

ui.page_config()
ui.title()
ui.setup_explanation()

uploaded_file = st.file_uploader("Choose a file", type=["mp4", "webm"])

if uploaded_file is not None:
    original_name, unique_id = ui.upload_file_to_azure(uploaded_file)

    blobs = [
        f"{unique_id}.json",
        f"{unique_id}.png",
        f"{unique_id}_normalgraph.png",
        f"{unique_id}_anglevalues.png",
        f"{unique_id}_yvalues.png",
    ]


    results = ui.download_results_from_azure(
        blobs, 
        message="""The model is processing the video.
        If this is your first upload, model start up can take up to 5 minutes.
        Any subsequent upload will take around 15 seconds.""", 
        balloons=True
    )

    recommendation, blob_data_json = ui.results_recommendation(results, unique_id)
    ui.results_methodology(results, unique_id)


    blobs_2 = [
        f"{unique_id}.json",
        f"{unique_id}_anglevideo.mp4",
    ]
    results_2 = ui.download_results_from_azure(blobs_2, message="A video is being created...", balloons=True)
    st.video(f"{unique_id}_anglevideo.mp4")

    ui.download_zip(results_2, original_name, unique_id)

    ui.follow_up(recommendation)
