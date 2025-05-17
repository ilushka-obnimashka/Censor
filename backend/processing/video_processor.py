import traceback
from typing import List, Optional

import cv2
from utils import pixelation_box, draw_box

from .model import model


def process_video(
        input_path: str,
        black_list: List[str],
        models_to_apply: List[str],
        pixelation: bool = True,
) -> Optional[List[any]]:
    """
    Process a video: detect and censor regions in frames.

    :param input_path: Path to input video.
    :param black_list: List of class names to censor.
    :param models_to_apply: Models to use.
    :param pixelation: Apply pixelation if True, else draw boxes.
    """
    try:
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise ValueError(f"Failed to open video {input_path}")

        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frames = []

        tracked_class_names = []
        frame_count = 0
        tracking_interval = max(fps // 2, 1)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % tracking_interval == 0:
                filtered_models = [m for m in models_to_apply if m != "bad_words_detector"]
                results = model(frame, filtered_models)
                trackers = cv2.legacy.MultiTracker_create()
                tracked_class_names.clear()

                for result in results:
                    class_name = result['class']
                    x1, y1, x2, y2 = result['box']
                    if class_name in black_list:
                        if pixelation:
                            pixelation_box(frame, x1, y1, x2, y2)
                        else:
                            draw_box(frame, x1, y1, x2, y2, class_name)

                        tracker = cv2.legacy.TrackerCSRT_create()
                        trackers.add(tracker, frame, (x1, y1, x2 - x1, y2 - y1))
                        tracked_class_names.append(class_name)
            else:
                success, boxes = trackers.update(frame)
                for i, newbox in enumerate(boxes):
                    class_name = tracked_class_names[i] if i < len(tracked_class_names) else "Tracked"
                    x, y, w, h = map(int, newbox)
                    if class_name in black_list:
                        if pixelation:
                            pixelation_box(frame, x, y, x + w, y + h)
                        else:
                            draw_box(frame, x, y, x + w, y + h, class_name)

            frames.append(frame)
            del frame
            frame_count += 1

        cap.release()
        return frames, fps
    except Exception as e:
        tb_str = traceback.format_exc()
        raise RuntimeError(f"Error processing video:\n{tb_str}")
        return None
