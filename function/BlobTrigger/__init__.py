import azure.functions as func
import logging
import json
import requests
import os


def main(myblob: func.InputStream):
    """Sends a request to the Machine learning model once activated by blob storage event
    Args:
        myblob: The data from the blob storage event
    """
    logging.info(
        f"Python blob trigger function processed blob \n"
        f"Name: {myblob.name}\n"
        f"Blob Size: {myblob.length} bytes"
    )

    model_url = os.environ["AZURE_ML_MODEL_ENDPOINT"]
    file_name = myblob.name.split("/")[1]

    headers = {"Content-Type": "application/json"}
    data = {"file_name": file_name}
    data = json.dumps(data)
    response = requests.request("POST", model_url, data=data, headers=headers)

    logging.info(f"{response}")
    logging.info(f"Send {file_name} to model @ {model_url}")