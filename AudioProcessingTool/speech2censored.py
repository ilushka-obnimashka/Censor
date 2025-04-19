import json
import math
import os

import click
from pydub import AudioSegment

from AudioProcessingTool.audio2text_timestamps import get_word_timestamps_vosk
from AudioProcessingTool.gigachat_integration import setup_gigachat_client, detect_profanity
from temp_file_manager import TempFilesManager

model_path = "resources/vosk-model-small-ru-0.22"
# Using a large model
# model_path = "vosk-model-ru-0.42"

# Using your authorization key for gigachat
AUTHORIZATION_KEY = "MDZlMGU2NzItZTBiMC00YTBjLThmN2ItZGE5ZWM4MTE4MGFiOjEyMWYyNDIzLTFlMzItNGY0Yi1hMWJlLTdhYmIxMjYyNTk1NA=="


def censor_audio(profanity_timestamps: list[dict[str, str | float]], orig_audio_path, censor_sound) -> None:
    """
    Censors profanity words in audio recordings.
    :param profanity_timestamps: list of profanity timestamps.
    :param orig_audio: path to original audio.
    :param censor_sound: path to censor sound.
    """

    orig_audio = AudioSegment.from_file(orig_audio_path)
    censor_sound = AudioSegment.from_file(censor_sound)

    censored_audio = AudioSegment.empty()
    profanity_timestamps = profanity_timestamps["profanity_timestamps"]

    last_position = 0

    for item in profanity_timestamps:
        start_ms = item["start"] * 1000  # in milliseconds
        end_ms = item["end"] * 1000
        duration = end_ms - start_ms

        censored_audio += orig_audio[last_position:start_ms]

        censor_segment = (censor_sound * math.ceil(duration / len(censor_sound)))[:duration]
        censored_audio += censor_segment

        last_position = end_ms

    censored_audio += orig_audio[last_position:]

    orig_basename = os.path.splitext(os.path.basename(orig_audio_path))[0]
    orig_format = os.path.splitext(os.path.basename(orig_audio_path))[1]
    output_filename = f"censor_{orig_basename}{orig_format}"

    censored_audio.export(output_filename, format=orig_format[1:])


@click.command()
@click.argument('input_file', type=click.Path(exists=True))
def main(input_file):
    """
    The main entrance point for processing audio files.
    :param input_file: The path to the input audio file.
    """
    try:
        timestamps = get_word_timestamps_vosk(model_path, input_file)
        print(f"timestamps: {timestamps}")
    except Exception as e:
        print(f"AudioError: {e}")
        exit(1)

    TempFilesManager().cleanup()

    client = setup_gigachat_client(AUTHORIZATION_KEY)
    result = json.loads(detect_profanity(client, timestamps))
    print(f"result: {result}")
    censor_audio(result, input_file, "AudioProcessingTool/resources/censor_sound.mp3")


if __name__ == "__main__":
    main()
