import os


def get_string_from_file(file_name):
    textfiles_path = os.path.join(os.path.dirname(__file__), "../../textfiles")
    with open(os.path.join(textfiles_path, file_name), "r") as f:
        string = f.read()
    return string


def get_image_path(file_name):
    return os.path.join(os.path.dirname(__file__), "../../images", file_name)
