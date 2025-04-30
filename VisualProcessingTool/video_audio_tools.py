import os

from moviepy import VideoFileClip, AudioFileClip

from AudioProcessingTool.audio2text_timestamps import audio_format_transcoder
from temp_file_manager import TempFilesManager


def extract_audio_from_video(video_path: str) -> str:
    """
    It extracts an audio track from a video file, converts it into a mono and sets the sampling frequency of 16khz, then
    saves in format .Wav
    """

    video_clip = VideoFileClip(video_path)
    audio_path = TempFilesManager().create_temp_file("temp.wav")
    video_clip.audio.write_audiofile(audio_path)

    return audio_format_transcoder(audio_path)


def replace_audio_in_video(new_audio_path: str, orig_video_path: str) -> None:
    """
    Replaces the audio track in a video file with a new audio file.
    """

    temp_video = TempFilesManager().create_temp_file(f"temp_{os.path.basename(orig_video_path)}")

    with VideoFileClip(orig_video_path) as video_clip, AudioFileClip(new_audio_path) as new_audio:
        original_audio = video_clip.audio

        if original_audio is not None:
            new_audio = (
                new_audio.set_fps(original_audio.fps)
                .set_duration(original_audio.duration)
                .set_channels(original_audio.channels)
            )

        video_with_new_audio = video_clip.set_audio(new_audio)
        video_with_new_audio.write_videofile(temp_video, threads=4)

    os.replace(temp_video, orig_video_path)
