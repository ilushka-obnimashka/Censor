from dotenv import load_dotenv

from .plugin_manager import PluginManager
from .detectors.base_detector import BaseDetector
from .detectors.bad_words_detector import BadWordsDetector
from .detectors.nude_detector import NudeDetector
from .detectors.cigarette_detector import CigaretteDetector
from .detectors.extremism_detector import ExtremismDetector

__all__ = [
    'PluginManager',
    'BaseDetector',
    'BadWordsDetector',
    'NudeDetector',
    'CigaretteDetector',
    'ExtremismDetector',
]

load_dotenv(".env")
default_plugin_manager = PluginManager()
default_plugin_manager.load_plugins()