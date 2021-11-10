import logging
import tensorflow as tf
import tensorflow_hub as tfhub
from utils.cropping import init_crop_region, determine_crop_region, crop_and_resize
from utils.utils import timeit


@timeit
def load_model_from_tfhub(model_name="movenet_thunder", version=4):
    """Loads the movenet model from tensorflow hub.

    Args:
      model_name: either 'movenet_thunder' or 'movenet_lighting'
      version: version of the model
    Returns:
      A model object and an input size int
    """
    if model_name == "movenet_lightning":
        module = tfhub.load(
            f"https://tfhub.dev/google/movenet/singlepose/lightning/{version}"
        )
        input_size = 192
    elif model_name == "movenet_thunder":
        module = tfhub.load(
            f"https://tfhub.dev/google/movenet/singlepose/thunder/{version}"
        )
        input_size = 256
    else:
        raise ValueError("Unsupported model name: %s" % model_name)

    model = module.signatures["serving_default"]
    # this prevents the python 3.8.x garbage collector from
    # deleting variable references if the model is stored in memory for a long time
    model._backref_to_saved_model = module
    return model, input_size


def _movenet(model, input_image):
    """Runs detection on an input image.

    Args:
      input_image: A [1, height, width, 3] tensor represents the input image
        pixels. Note that the height/width should already be resized and match the
        expected input resolution of the model before passing into this function.
    Returns:
      A [17, 3] float numpy array representing the predicted keypoint
      coordinates and scores. The keypoint-order is shown in KEYPOINT_DICT.
      The 3 results are {y, x, confidence}.
    """
    # SavedModel format expects tensor type of int32.
    outputs = model(input=tf.cast(input_image, dtype=tf.int32))
    # output_0 is a [1,1,17, 3] array
    keypoint_with_scores = outputs["output_0"].numpy()
    return keypoint_with_scores.squeeze()


def _run_inference(model, image, crop_region, crop_size):
    """Runs model inferece on the cropped region. The function runs the model inference on the cropped region and updates the
    model output to the original image coordinate system.

    Args:
      model: the model to use
      image: the image to run inference on
      crop_region: the region of the image to crop the image to
      crop_size: the size
    Returns:
      (17,3) array of the keypoints
    """
    image_height, image_width, _ = image.shape
    input_image = crop_and_resize(
        tf.expand_dims(image, axis=0), crop_region, crop_size=crop_size
    )
    # Run model inference.
    keypoints_with_scores = _movenet(model, input_image)
    # Update the coordinates.
    for idx in range(17):
        keypoints_with_scores[idx, 0] = (
            crop_region["y_min"] * image_height
            + crop_region["height"] * image_height * keypoints_with_scores[idx, 0]
        ) / image_height
        keypoints_with_scores[idx, 1] = (
            crop_region["x_min"] * image_width
            + crop_region["width"] * image_width * keypoints_with_scores[idx, 1]
        ) / image_width
    return keypoints_with_scores


@timeit
def get_keypoints_from_video(video_tensor, model, input_size):
    """Runs model inference on each frame of a video, returning a list of keypoints.

    Args:
      video_tensor: input tensor for the model of shape [B, H, W, C]
      model: model object to use for frame-by-frame inference
      input_size: input size of the model (used for cropping and resizing)
    Returns:
      a [B, 17, 3] list of keypoint arrays, one array per frame in the video
    """
    num_frames, video_height, video_width, _ = video_tensor.shape
    all_keypoints_with_scores = []
    crop_region = init_crop_region(video_height, video_width)
    for frame_idx in range(num_frames):
        all_keypoints_with_scores.append(
            _run_inference(
                model,
                video_tensor[frame_idx, :, :, :],
                crop_region,
                crop_size=[input_size, input_size],
            )
        )
        crop_region = determine_crop_region(
            all_keypoints_with_scores[frame_idx], video_height, video_width
        )

    logging.info("Calculated all keypoints")
    return all_keypoints_with_scores
