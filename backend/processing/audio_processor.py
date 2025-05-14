import traceback
from typing import Optional

from .model import model


def process_audio(
        input_path: str) -> Optional[any]:
    """
    Process on a audio (это может быть как обработка аудио из файла, так и самостоятельный аудиофайл)
    :param input_path: Path to the input file (video or audio)
    """
    try:
        censored_audio_path = model(input_path, ['bad_words_detector'])
        return ''.join(censored_audio_path)
    except Exception as e:
        raise RuntimeError(f"Error processing audio: {traceback.format_exc()}")
