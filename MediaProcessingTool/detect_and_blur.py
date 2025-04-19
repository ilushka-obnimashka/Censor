import mimetypes
import random
from typing import Any, List, Tuple, Optional, Union

import click
import cv2

import censore_models

ALL_MODELS: dict[str, list[str]] = {
    'cigarette': ["cigarette"],
    'nude': [
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
    'extremism': [
        'lgbt',
        'svastika'
    ]
}


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

    if 'cigarette' in models_to_apply:
        results.extend(censore_models.cigarette(img))
    if 'nude' in models_to_apply:
        results.extend(censore_models.nude(img))
    if 'alcohol' in models_to_apply:
        results.extend(censore_models.alcohol(img))
    if 'extremism' in models_to_apply:
        results.extend(censore_models.extremism(img))

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


def process_file(
        input_path: str,
        output_path: str,
        black_list: List[str],
        pixelation: bool = True,
        show: bool = False
) -> None:
    """
    Automatically process image or video file.

    :param input_path: Path to media file.
    :param output_path: Path to save the result.
    :param black_list: List of classes to censor.
    :param pixelation: Use pixelation instead of drawing boxes.
    :param show: Show media while processing.
    """
    try:
        mime_type, _ = mimetypes.guess_type(input_path)
        if mime_type is None:
            raise ValueError("Unknown file format")

        if output_path is None and not show:
            raise ValueError("No output or display option specified")

        models_to_apply = [
            model for model, classes in ALL_MODELS.items()
            if any(cls in black_list for cls in classes)
        ]

        if mime_type.startswith('image'):
            result = process_image(input_path, black_list, models_to_apply, pixelation)
            if show:
                cv2.imshow("Processed Image", result)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            if output_path:
                save_output(result, output_path)

        elif mime_type.startswith('video'):
            frames, fps = process_video(input_path, black_list, models_to_apply, pixelation)
            if show:
                for frame in frames:
                    cv2.imshow("Processed Video", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                cv2.destroyAllWindows()
            if output_path:
                save_output(frames, output_path, fps)

        else:
            raise ValueError("File is not an image or video")

    except Exception as e:
        print(f"[ERROR] {e}")


@click.group()
def cli() -> None:
    """Main CLI entry point."""
    pass


@cli.command(help="Process media with censorship.")
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
def parse(
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
    cli()
