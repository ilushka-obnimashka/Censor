import mimetypes
import random
from typing import Any, List, Tuple, Optional, Union
import os

import click
import cv2

from plugin_manager import PluginManager
from processes import process_image, process_video, process_audio
from video_audio_tools import *

ALL_MODELS: dict[str, list[str]] = {
    "cigarette_detector": ["cigarette"],
    "nude_detector": [
        "FEMALE_GENITALIA_COVERED",
        "FACE_FEMALE",
        "BUTTOCKS_EXPOSED",
        "FEMALE_BREAST_EXPOSED",
        "FEMALE_GENITALIA_EXPOSED",
        "MALE_BREAST_EXPOSED",
        "ANUS_EXPOSED",
        "FEET_EXPOSED",
        "BELLY_COVERED",
        "FEET_COVERED",
        "ARMPITS_COVERED",
        "ARMPITS_EXPOSED",
        "FACE_MALE",
        "BELLY_EXPOSED",
        "MALE_GENITALIA_EXPOSED",
        "ANUS_COVERED",
        "FEMALE_BREAST_COVERED",
        "BUTTOCKS_COVERED"
    ],
    "extremism_detector": [
        "lgbt",
        "svastika"
    ],
    "bad_words_detector" : ["bad_words"]
}

PLUGIN_MANAGER = PluginManager()
PLUGIN_MANAGER.load_plugins()

print(PLUGIN_MANAGER._detectors)

def get_color(class_name: str) -> Tuple[int, int, int]:
    """
    Generate a deterministic color based on class name.

    :param class_name: The name of the class.
    :return: RGB tuple.
    """
    random.seed(class_name)
    return (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )


def draw_box(img: Any, x1: int, y1: int, x2: int, y2: int, label: str) -> None:
    """
    Draw a rectangle and label on the image.

    :param img: Image to draw on.
    :param x1, y1, x2, y2: Coordinates of the box.
    :param label: Label text.
    """
    color = get_color(label)
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
    cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


def pixelation_box(img: Any, x1: int, y1: int, x2: int, y2: int) -> None:
    """
    Apply pixelation to a region of the image.

    :param img: Input image.
    :param x1, y1, x2, y2: Box coordinates.
    """
    h, w = img.shape[:2]
    x1 = max(0, x1 - 5)
    y1 = max(0, y1 - 5)
    x2 = min(w, x2 + 5)
    y2 = min(h, y2 + 5)

    roi = img[y1:y2, x1:x2]
    if roi.size == 0:
        return

    roi_h, roi_w = roi.shape[:2]
    new_w = int(3 * round(roi_w / min(roi_w, roi_h)))
    new_h = int(3 * round(roi_h / min(roi_w, roi_h)))

    roi = cv2.resize(roi, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    roi = cv2.resize(roi, (roi_w, roi_h), interpolation=cv2.INTER_NEAREST)
    img[y1:y2, x1:x2] = roi


def model(img: Any, models_to_apply: List[str]) -> List[dict[str, Any]]:
    """
    Run selected models on the image.

    :param img: Image to process.
    :param models_to_apply: List of model names.
    :return: List of detection results.
    """
    results = []
    for model in models_to_apply:
        if model not in ALL_MODELS.keys():
            print(f"\033[93mWarning: Unknown model category '{model}'\033[0m")
            continue
        try:
            detector = PLUGIN_MANAGER.get_detector(model)
            results.extend(detector.detect(img))
        except ValueError as e:
            print(f"Warning: {e}")
    return results


def save_output(output: Union[List, any], output_path: str, fps: Optional[int] = None) -> None:
    """
    Save processed image or video frames to a file.

    :param output: Processed image (numpy array) or list of frames.
    :param output_path: Path to save the output.
    :param fps: FPS for video saving (required if saving video).
    """
    if isinstance(output, list):  # video
        height, width = output[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        for frame in output:
            out.write(frame)
        out.release()
    else:  # image
        cv2.imwrite(output_path, output)

def process_file(
        input_path: str,
        black_list: List[str],
        pixelation: bool = True,
        show: bool = False
) -> str:
    """
    Automatically process image or video file.

    :param input_path: Path to media file.
    :param output_path: Path to save the result.
    :param black_list: List of classes to censor.
    :param pixelation: Use pixelation instead of drawing boxes.
    :return : censored output path
    """

    orig_basename = os.path.splitext(os.path.basename(input_path))[0]
    orig_format = os.path.splitext(os.path.basename(input_path))[1]
    output_filename = f"censor_{orig_basename}{orig_format}"

    try:
        mime_type, _ = mimetypes.guess_type(input_path)
        if mime_type is None:
            raise ValueError("Unknown file format")

        models_to_apply = [
            model for model, classes in ALL_MODELS.items()
            if any(cls in black_list for cls in classes)
        ]

        if mime_type.startswith('image'):
            result = process_image(input_path, black_list, models_to_apply, pixelation)
            save_output(result, output_filename)

        elif mime_type.startswith('video'):
            frames, fps = process_video(input_path, black_list, models_to_apply, pixelation)
            save_output(frames, output_filename, fps)

            if "bad_words_detector" in models_to_apply:
                censor_audio_path = process_audio(input_path, True)
                replace_audio_in_video(censor_audio_path, output_filename)

        elif mime_type.startswith('audio'):
            output_filename = process_audio(input_path, False)
            TempFilesManager().cleanup()

        else:
            raise ValueError("File is not an image or video")

        return output_filename

    except Exception as e:
        print(f"[ERROR] {e}")


@click.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.option(
    "--black-list", "-b", multiple=True, required=True,
    help="Classes to censor (e.g. --black-list cigarette --black-list MALE_GENITALIA_EXPOSED)"
)
@click.option(
    "--pixelation/--no-pixelation", default=True,
    help="Pixelate or draw bounding boxes."
)
@click.option("--output-path", "-o", type=click.Path(), help="Output file path.")
@click.option("--show", is_flag=True, help="Display processing result in real-time.", hidden=True)
def main(
        input_path: str,
        output_path: Optional[str],
        black_list: Tuple[str, ...],
        pixelation: bool,
        show: bool
) -> None:
    """
    Parse the input media and apply censorship.
    """
    process_file(input_path, output_path, list(black_list), pixelation, show)


if __name__ == "__main__":
    main()
