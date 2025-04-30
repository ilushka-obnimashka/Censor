from typing import Optional

from .model import model
from utils import extract_audio_for_vosk


def process_audio(
        input_path: str,
        is_video: bool) -> Optional[any]:
    """
    Process on a audio (это может быть как обработка аудио из файла, так и самостоятельный аудиофайл)
    :param input_path: Path to the input file (video or audio)
    """
    try:
        if is_video:
            input_path = extract_audio_for_vosk(input_path)
        censored_audio_path = model(input_path, ['bad_words_detector'])
        return ''.join(censored_audio_path)
    except Exception as e:
        raise RuntimeError(f"Error processing audio: {e}")
