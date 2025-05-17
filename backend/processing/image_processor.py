import os
import traceback
from typing import List, Optional

import cv2
from utils import TempFilesManager, pixelation_box, draw_box

from .model import model


def process_image(
        input_path: str,
        black_list: List[str],
        models_to_apply: List[str],
        pixelation: bool = True,
) -> Optional[any]:
    """
    Process an image: detect and censor regions.

    :param input_path: Path to input image.
    :param black_list: List of class names to censor.
    :param models_to_apply: Models to use.
    :param pixelation: Apply pixelation if True, else draw boxes.
    """
    try:
        orig_name, orig_format = os.path.splitext(os.path.basename(input_path))
        output_path = TempFilesManager().create_temp_file(f"{orig_name}_censor_video{orig_format}")

        image = cv2.imread(input_path)
        if image is None:
            raise ValueError(f"Failed to read image from {input_path}")
        results = model(image, models_to_apply)

        for result in results:
            class_name = result['class']
            x1, y1, x2, y2 = result['box']
            if class_name in black_list:
                if pixelation:
                    pixelation_box(image, x1, y1, x2, y2)
                else:
                    draw_box(image, x1, y1, x2, y2, class_name)
        cv2.imwrite(output_path, image)
        return output_path
    except Exception as e:
        raise RuntimeError(f"Error processing image: {traceback.format_exc()}")
