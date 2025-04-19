import torch
from nudenet import NudeDetector
from ultralytics import YOLO

IMAGE_SIZE = 640  # All images are resized to this dimension before being fed into the model
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def cigarette(img):
    """
    Detects cigarettes in the given image using a trained YOLO model.

    :param img: Input image (path or array).
    :return: List of detected objects with class name and bounding box.
    """
    model = YOLO('models/cigarette.pt')
    results = model(img, imgsz=(IMAGE_SIZE, IMAGE_SIZE), device=DEVICE, iou=0.65)
    parsed = []

    names = results[0].names
    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        class_name = names[int(box.cls[0])]
        parsed.append({'class': class_name, 'box': (x1, y1, x2, y2)})

    return parsed


def nude(img):
    """
    Detects nudity in the given image using NudeNet.

    :param img: Input image (path or array).
    :return: List of detected objects with class name and bounding box.
    """
    model = NudeDetector(model_path="models/nudenet640m.onnx", inference_resolution=IMAGE_SIZE)
    results = model.detect(img)
    parsed = []

    for result in results:
        class_name = result['class']
        x, y, w, h = result['box']
        x1, y1, x2, y2 = x, y, x + w, y + h
        parsed.append({'class': class_name, 'box': (x1, y1, x2, y2)})

    return parsed


def alcohol(img):
    """
    Stub function for detecting alcohol in the image.

    :param img: Input image.
    """
    pass  # To be implemented


def extremism(img):
    """
    Detects extremist symbols in the given image using a trained YOLO model.

    :param img: Input image (path or array).
    :return: List of detected objects with class name and bounding box.
    """
    model = YOLO('models/extremism.pt')
    results = model(img, imgsz=(IMAGE_SIZE, IMAGE_SIZE), device=DEVICE, iou=0.65)
    parsed = []

    names = results[0].names
    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        class_name = names[int(box.cls[0])]
        parsed.append({'class': class_name, 'box': (x1, y1, x2, y2)})

    return parsed
