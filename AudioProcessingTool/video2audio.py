from moviepy import VideoFileClip

from AudioProcessingTool.audio2text_timestamps import audio_format_transcoder
from temp_file_manager import TempFilesManager


def video2audio(video_path: str) -> str:
    """
    It extracts an audio track from a video file, converts it into a mono and sets the sampling frequency of 16khz, then
    saves in format .Wav
    """

    video_clip = VideoFileClip(video_path)
    audio_path = TempFilesManager().create_temp_file("temp.wav")
    video_clip.audio.write_audiofile(audio_path)

    return audio_format_transcoder(audio_path)
