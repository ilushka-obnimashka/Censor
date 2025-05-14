import random
from typing import Any, Tuple

import cv2


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
