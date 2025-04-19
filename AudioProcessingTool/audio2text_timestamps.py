import contextlib
import json
import os.path
import wave

from pydub import AudioSegment
from vosk import Model, KaldiRecognizer

from temp_file_manager import TempFilesManager


def audio_format_transcoder(audio_path: str) -> str:
    """
    Converts an audio file in WAV with a frequency of 16 kHz and mono.

    :param audio_path: the path to the original audio file.
    :return: the path to a converted temporary file in WAV format.
    :raises RuntimeError: if the conversion has failed.
    """
    output_path = TempFilesManager().create_temp_file(f"{os.path.splitext(os.path.basename(audio_path))[0]}.wav")

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


def get_word_timestamps_vosk(model_path: str, audio_path: str) -> list[dict[str, str | float]]:
    """
    Removes temporary marks of words from the audio file using the VOSK model.

    :param audio_path: The path to the audio file for processing.
    :return: A list of dictionaries containing information about words and their time tags.
    """

    try:
        correct_format_audio = audio_format_transcoder(audio_path)
    except RuntimeError as e:
        raise RuntimeError(f"Could not convert audio file: {str(e)}") from e

    try:
        model = Model(model_path)
        rec = KaldiRecognizer(model, 16000)
    except Exception as e:
        error = f"ModelError: {str(e)}"
        raise RuntimeError(error)

    rec.SetWords(True)

    with wave.open(correct_format_audio, 'rb') as audio_file:
        results = []
        while True:
            data = audio_file.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                part_result = json.loads(rec.Result())
                results.append(part_result)

        final_result = json.loads(rec.FinalResult())
        results.append(final_result)

    word_timestamps = []
    for res in results:
        if 'result' in res:
            for word_info in res['result']:
                word_timestamps.append({
                    'word': word_info['word'],
                    'start': word_info['start'],
                    'end': word_info['end']
                })

    return word_timestamps
