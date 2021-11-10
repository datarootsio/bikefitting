def get_file_extension(uploaded_file):
    if uploaded_file.type == "video/webm":
        return "webm"
    elif uploaded_file.type == "video/mp4":
        return "mp4"
    else:
        return "mov"


def interpret_model_recommendation(recommendation):
    if recommendation == "UP":
        recommendation = "raise"
        pointer = "+"
    elif recommendation == "DOWN":
        recommendation = "lower"
        pointer = "-"
    else:
        recommendation = "don't change"
        pointer = ""
    return recommendation, pointer
