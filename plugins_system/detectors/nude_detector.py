from typing import Any, List, Dict

from nudenet import NudeDetector as OrigNudeDetector

from .base_detector import *


class NudeDetector(BaseDetector):
    def __init__(self, device: str = 'cuda'):
        super().__init__('models/nudenet640m.onnx', device)
        self.model = OrigNudeDetector(model_path=self.model_path, inference_resolution=IMAGE_SIZE)

    def detect(self, img: Any) -> List[Dict[str, Any]]:
        """
        Detects nudity in the given image using NudeNet.

        :param img: Input image (path or array).
        :return: List of detected objects with class name and bounding box.
        """
        results = self.model.detect(img)
        parsed = []

        for result in results:
            class_name = result['class']
            x, y, w, h = result['box']
            x1, y1, x2, y2 = x, y, x + w, y + h
            parsed.append({'class': class_name, 'box': (x1, y1, x2, y2)})

        return parsed
