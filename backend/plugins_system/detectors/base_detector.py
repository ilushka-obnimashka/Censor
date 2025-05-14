from abc import ABC, abstractmethod
from typing import Any, List, Dict

import torch

IMAGE_SIZE = 640  # All images are resized to this dimension before being fed into the model
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class BaseDetector(ABC):
    def __init__(self, model_path: str, device: str = '0'):
        self.model = None
        self.model_path = model_path
        self.device = device

    @abstractmethod
    def detect(self, img: Any) -> List[Dict[str, Any]]:
        pass
