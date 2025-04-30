import contextlib
import os
import wave
from time import sleep

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
    output_path = TempFilesManager().create_temp_file("temp.wav")

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
        raise RuntimeError(f"AudioConversionError: {str(e)}")


def extract_audio_for_vosk(video_path: str) -> str:
    """
    Извлекает аудио из видео, конвертирует в моно WAV с частотой 16 кГц,
    возвращает путь к аудиофайлу, готовому для Vosk.
    """
    orig_basename = os.path.splitext(os.path.basename(video_path))[0]
    vosk_audio_path = TempFilesManager().create_temp_file(f"{orig_basename}.wav")
    temp_audio_path = TempFilesManager().create_temp_file("temp_extracted_audio.wav")

    with VideoFileClip(video_path) as video_clip:
        video_clip.audio.write_audiofile(temp_audio_path, codec='pcm_s16le')

    audio = AudioSegment.from_file(temp_audio_path)
    audio = audio.set_frame_rate(16000).set_channels(1)

    audio.export(vosk_audio_path, format="wav")

    return vosk_audio_path


def add_audio_to_video(audio_path: str, video_path: str) -> None:
    """
    Заменяет или добавляет аудио в видеофайл, сохраняя исходный путь.
    Работает даже если в видео изначально нет аудиодорожки.
    """

    temp_output = f"temp_{video_path}" # создали временный файл, который потом будет перемещен
    TempFilesManager().create_temp_file(temp_output)

    try:
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)

        final_clip = video.set_audio(audio)

        final_clip.write_videofile(
            temp_output,
            codec='libx264',
            audio_codec='aac',
            threads=4,
            verbose=False
        )

        video.close()
        audio.close()

        os.replace(temp_output, video_path)

    except Exception as e:
        if os.path.exists(temp_output):
            os.remove(temp_output)
        raise RuntimeError(f"Ошибка замены аудио: {str(e)}")

