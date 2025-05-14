import importlib
import os
from pathlib import Path
from typing import Dict

from plugins_system.detectors.base_detector import BaseDetector


class PluginManager:

    def __init__(self, plugins_dir: str = "backend/plugins_system/detectors"):
        self.__plugins_dir = Path(plugins_dir)
        self.__detectors: Dict[str, BaseDetector] = {}

    def load_plugins(self):
        target_pattern = "*.py"
        for file in self.__plugins_dir.glob(target_pattern):
            plugin_name = os.path.splitext(os.path.basename(file))[0]
            if plugin_name.startswith("_"):
                continue
            module = importlib.import_module(f"plugins_system.detectors.{plugin_name}")

            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if (
                        isinstance(attribute, type) and
                        issubclass(attribute, BaseDetector) and
                        attribute != BaseDetector
                ):
                    plugin = plugin_name.lower()
                    self.__detectors[plugin] = attribute()

    def get_detector(self, plugin_name: str) -> BaseDetector:
        if plugin_name not in self.__detectors:
            raise Exception(f"Plugin '{plugin_name}' not found")
        return self.__detectors[plugin_name]
