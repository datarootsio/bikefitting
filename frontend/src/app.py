"""
This file represents the website interface used to:
- upload videos for the backend to analyze
- and display the results to the user.
The website is built with streamlit.
"""
import streamlit as st
from utils import ui
import logging

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
        f"{unique_id}_anglevideo.webm",
    ]

    results = ui.download_results_from_azure(blobs)

    recommendation, blob_data_json = ui.results_recommendation(results, unique_id)
    ui.results_methodology(results, unique_id)
    ui.results_videoplot(results, blob_data_json, unique_id)

    ui.download_zip(results, original_name, unique_id)

    ui.follow_up(recommendation)
