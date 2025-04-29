import importlib
import os
from pathlib import Path
from typing import Dict

from plugins.base_detector import BaseDetector


class PluginManager:

    def __init__(self, plugins_dir: str = "/home/ilushka-obnimashka/Desktop/Censor/VisualProcessingTool/plugins"):
        self.plugins_dir_ = Path(plugins_dir)
        self._detectors: Dict[str, BaseDetector] = {}

    def load_plugins(self):
        target_pattern = "*.py"
        for file in self.plugins_dir_.glob(target_pattern):
            plugin_name = os.path.splitext(os.path.basename(file))[0]
            if plugin_name.startswith("_"):
                continue
            module = importlib.import_module(f"plugins.{plugin_name}")

            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if (
                        isinstance(attribute, type) and
                        issubclass(attribute, BaseDetector) and
                        attribute != BaseDetector
                ):
                    plugin = plugin_name.lower()
                    self._detectors[plugin] = attribute()

    def get_detector(self, plugin_name: str) -> BaseDetector:
        if plugin_name not in self._detectors:
            raise Exception(f"Plugin '{plugin_name}' not found")
        return self._detectors[plugin_name]
