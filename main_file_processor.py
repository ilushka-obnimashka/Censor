import mimetypes
import os
import traceback
from typing import List, Optional, Union

import cv2

from processing import process_image, process_video, process_audio
from utils import TempFilesManager, add_audio_to_video
from models_config import ALL_MODELS



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
) -> str:
    """
    Automatically process image or video file.

    :param input_path: Path to media file.
    :param black_list: List of classes to censor.
    :param pixelation: Use pixelation instead of drawing boxes.
    :return : censored output path
    """

    orig_name, orig_format = os.path.splitext(os.path.basename(input_path))
    output_filename = os.path.join(os.path.dirname(input_path), f"{orig_name}_censor{orig_format}")

    try:
        mime_type, _ = mimetypes.guess_type(input_path)
        if mime_type is None:
            raise ValueError("Unknown file format")

        if black_list:
            models_to_apply = [
                model for model, classes in ALL_MODELS.items()
                if any(cls in black_list for cls in classes)
            ]
        else:
            models_to_apply = list(ALL_MODELS.keys())
            black_list = [value for values in ALL_MODELS.values() for value in values]

        if mime_type.startswith('image'):
            if "bad_words_detector" in models_to_apply:
                models_to_apply = [m for m in models_to_apply if m != "bad_words_detector"]

            result = process_image(input_path, black_list, models_to_apply, pixelation)
            save_output(result, output_filename)

        elif mime_type.startswith('video'):
            frames, fps = process_video(input_path, black_list, models_to_apply, pixelation)
            temp_output_filename = TempFilesManager().create_temp_file(f"{orig_name}_censor_video{orig_format}")
            save_output(frames, temp_output_filename, fps)

            audio_path = extract_audio(input_path)
            if "bad_words_detector" in models_to_apply:
                audio_path = process_audio(audio_path)

            add_audio_to_video(audio_path, temp_output_filename, output_filename)

        elif mime_type.startswith('audio'):
            audio_path = process_audio(input_path)
            os.replace(audio_path, output_filename)

        else:
            raise ValueError("File is not an image or video")

        return output_filename

    except Exception as e:
        print(f"[ERROR] {traceback.format_exc()}")
