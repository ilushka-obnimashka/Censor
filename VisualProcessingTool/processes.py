from typing import List, Optional

import cv2

from detect_and_blur import model, pixelation_box, draw_box
from video_audio_tools import extract_audio_from_video


def process_audio(
        input_path: str,
        is_video: bool) -> Optional[any]:
    """
    Process on a audio (это может быть как обработка аудио из файла, так и самостоятельный аудиофайл)
    :param input_path: Path to the input file (video or audio)
    """
    try:
        if is_video:
            input_path = extract_audio_from_video(input_path)
        censored_audio_path = model(input_path, "bad_words_detector")
        return censored_audio_path
    except Exception as e:
        raise RuntimeError(f"Error processing audio: {e}")


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
        return image
    except Exception as e:
        raise RuntimeError(f"Error processing image: {e}")


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

        trackers = cv2.legacy.MultiTracker_create()
        tracked_class_names = []
        frame_count = 0
        tracking_interval = max(fps // 2, 1)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % tracking_interval == 0:
                results = model(frame, models_to_apply)
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
            frame_count += 1

        cap.release()
        return frames, fps
    except Exception as e:
        raise RuntimeError(f"Error processing video: {e}")
        return None
