import os

import onnxruntime
from nudenet import NudeDetector as OrigNudeDetector

from .base_detector import *


class CustomNudeDetector(OrigNudeDetector):
    def __init__(self, model_path=None, providers=None, inference_resolution=320):
        onnxruntime.preload_dlls(cuda=True, cudnn=True)
        self.onnx_session = onnxruntime.InferenceSession(
            os.path.join(os.path.dirname(__file__), "320n.onnx")
            if not model_path
            else model_path,
            providers=["CUDAExecutionProvider", 'CPUExecutionProvider'],
        )
        model_inputs = self.onnx_session.get_inputs()

        self.input_width = inference_resolution
        self.input_height = inference_resolution
        self.input_name = model_inputs[0].name


class NudeDetector(BaseDetector):
    def __init__(self, device: str = 'cuda'):
        super().__init__('backend/models/nudenet640m.onnx', device)
        self.model = CustomNudeDetector(model_path=self.model_path, inference_resolution=IMAGE_SIZE)

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
