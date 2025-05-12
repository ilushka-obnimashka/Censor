import contextlib
import os
import traceback
import wave

from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment

from .temp_file_manager import TempFilesManager


def audio_format_transcoder(audio_path: str) -> str:
    """
    Converts an audio file in WAV with a frequency of 16 kHz and mono.

    :param audio_path: the path to the original audio file.
    :return: the path to a converted temporary file in WAV format.
    :raises RuntimeError: if the conversion has failed.
    """

    orig_name = os.path.splitext(os.path.basename(audio_path))[0]
    output_path = TempFilesManager().create_temp_file(f"{orig_name}_vosk.wav")

    try:
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(
            output_path,
            format="wav",
            codec="pcm_s16le",
            parameters=["-ar", "16000", "-ac", "1"]
        )
        with contextlib.closing(wave.open(output_path, 'r')) as wav:
            if wav.getnchannels() != 1:
                raise ValueError("The wrong number of channels")
        return output_path

    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        raise RuntimeError(f"AudioConversionError: {traceback.format_exc()}")


def extract_audio(video_path: str) -> str:
    """
    Извлекает аудио из видео
    возвращает путь к аудиофайлу.
    """
    orig_basename = os.path.splitext(os.path.basename(video_path))[0]
    orig_audio_path = TempFilesManager().create_temp_file(f"{orig_basename}.wav")

    with VideoFileClip(video_path) as video_clip:
        video_clip.audio.write_audiofile(orig_audio_path, codec='pcm_s16le')

    return orig_audio_path


def add_audio_to_video(audio_path: str, video_path: str, output_path: str) -> None:
    """
    Добавляет или заменяет аудио в видеоролике и сохраняет результат в output_path.

    :param audio_path: Путь к аудиофайлу (mp3, wav и т.п.)
    :param video_path: Путь к исходному видеофайлу
    :param output_path: Путь, по которому сохранить финальный файл с аудио
    """

    try:
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)

        final_clip = video.set_audio(audio)

        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            threads=4,
            verbose=False
        )

        video.close()
        audio.close()

    except Exception as e:
        raise RuntimeError(f"Ошибка замены аудио: {traceback.format_exc()}")
