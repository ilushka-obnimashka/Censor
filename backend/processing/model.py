import traceback
from typing import Any, List

from plugins_system import default_plugin_manager


def model(media: Any, models_to_apply: List[str]) -> List[dict[str, Any]]:
    """
    Run selected models on the image.

    :param img: Image to process.
    :param models_to_apply: List of model names.
    :return: List of detection results.
    """
    results = []
    for model in models_to_apply:
        try:
            detector = default_plugin_manager.get_detector(model)
            results.extend(detector.detect(media))
        except ValueError as e:
            print(f"Warning: {traceback.format_exc()}")
    return results
