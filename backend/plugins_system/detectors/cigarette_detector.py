from ultralytics import YOLO
import os

from .base_detector import *


class CigaretteDetector(BaseDetector):
    def __init__(self):
        super().__init__(os.path.abspath('backend/models/cigarette.pt'))
        self.model = YOLO(self.model_path)

    def detect(self, img: Any) -> List[Dict[str, Any]]:
        """
        Detects cigarettes in the given image using a trained YOLO model.

        :param img: Input image (path or array).
        :return: List of detected objects with class name and bounding box.
        """
        results = self.model(img, imgsz=(IMAGE_SIZE, IMAGE_SIZE), device=self.device, iou=0.65)
        parsed = []

        names = results[0].names
        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_name = names[int(box.cls[0])]
            parsed.append({'class': class_name, 'box': (x1, y1, x2, y2)})

        return parsed
