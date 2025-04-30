import contextlib
import json
import math
import os.path
import wave

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat import GigaChat
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer

from temp_file_manager import TempFilesManager
from .base_detector import *


class BadWordsDetector(BaseDetector):
    def __init__(self, device: str = 'cuda'):
        super().__init__('VisualProcessingTool/models/vosk-model-small-ru-0.22', device)
        self.model_ = Model(self.model_path)
        self.recognizer_ = KaldiRecognizer(self.model, 16000)
        self.giga_client_ = self.setup_gigachat_client(AUTHORIZATION_KEY)

    def detect (self, media: Any) -> List[Dict[str, Any]]:
        """
        Detects In the Given Audio Using a Trained Vosk Model and Gigachat LLM API, obscene vocabulary.

        :param media: Input audio path.
        :return: path for output audio file.
        """
        try:
            timestamps = self.get_word_timestamps_vosk(media)
        except Exception as e:
            print(f"AudioError: {e}")
            exit(1)

        result = json.loads(self.detect_profanity(timestamps))

        return self.censor_audio(result, media, "AudioProcessingTool/resources/censor_sound.mp3")

    def audio_format_transcoder(self, audio_path: str) -> str:
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

    def get_word_timestamps_vosk(self, audio_path: str) -> list[dict[str, str | float]]:
        """
        Removes temporary marks of words from the audio file using the VOSK model.

        :param audio_path: The path to the audio file for processing.
        :return: A list of dictionaries containing information about words and their time tags.
        """
        try:
            correct_format_audio = self.audio_format_transcoder(audio_path)
        except RuntimeError as e:
            raise RuntimeError(f"Could not convert audio file: {str(e)}") from e

        self.recognizer_.SetWords(True)

        with wave.open(correct_format_audio, 'rb') as audio_file:
            results = []
            while True:
                data = audio_file.readframes(4000)
                if len(data) == 0:
                    break
                if self.recognizer_.AcceptWaveform(data):
                    part_result = json.loads(self.recognizer_.Result())
                    results.append(part_result)

            final_result = json.loads(self.recognizer_.FinalResult())
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

    def setup_gigachat_client(self, auth_token: str) -> GigaChat:
        """
        Sets up the GigaChat client with secure settings.
        :param auth_token: The authentication token for the GigaChat API.
        :return: Configured GigaChat client instance.
        """
        return GigaChat(
            credentials=auth_token,
            model="GigaChat-2",
            verify_ssl_certs=False,
            temperature=0.1,  # Low temperature for more precise responses
            scope="GIGACHAT_API_PERS"
        )

    def prepare_profanity_detection_prompt(self, timestamps_words: list[dict[str, float]]) -> str:
        """
        Prepares a prompt for detecting profanity words.
        :param timestamps_words: A list of dictionaries containing word information and their timestamps.
        :return: A formatted text message for profanity detection.
        """
        words_str = "\n".join([
            f"Word: {word['word']}, Start: {word['start']}, End: {word['end']}"
            for word in timestamps_words
        ])

        return f"""
    Твоя задача - проанализировать следующий список слов и определить, 
    какие из них являются матерными. Для каждого матерного слова верни 
    JSON с его временными метками:

    {words_str}

    Верни результат в формате JSON:
    {{
        "profanity_timestamps": [
            {{
                "word": "матерное_слово",
                "start": начало_метки,
                "end": конец_метки
            }},
            ...
        ]
    }}

    Если матерных слов нет, верни пустой список.
    """

    def detect_profanity(self, timestamps_words: list[dict[str, float]]) -> list[dict[str, float]]:
        """
        Detects profanity words using the GigaChat client.

        :param timestamps_words: A list of dictionaries containing word information and their timestamps.
        :return: A list of dictionaries with profanity words and their timestamps.
                 Returns `None` if an error occurs during the request.
        """
        prompt = self.prepare_profanity_detection_prompt(timestamps_words)

        print(prompt)

        messages = [
            SystemMessage(content="Ты помощник, который точно определяет матерные слова."),
            HumanMessage(content=prompt)
        ]

        try:
            response = self.giga_client_.invoke(messages)
            return response.content[7:-3]
        except Exception as e:
            print(f"Error during request: {e}")
            return None

    def censor_audio(self, profanity_timestamps: list[dict[str, str | float]], orig_audio_path, censor_sound) -> str:
        """
        Censors profanity words in audio recordings.
        :param profanity_timestamps: list of profanity timestamps.
        :param orig_audio: path to original audio.
        :param censor_sound: path to censor sound.
        :return output_filename : path to the censorned audio.
        """

        orig_audio = AudioSegment.from_file(orig_audio_path)

        censor_sound = AudioSegment.from_file(censor_sound)
        censor_sound = (
            censor_sound
            .set_sample_width(orig_audio.sample_width )
            .set_frame_rate(orig_audio.frame_rate)
            .set_channels(orig_audio.channels)
        )

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

        censored_audio.export(
            output_filename,
            format=orig_format[1:],
            bitrate=orig_audio.frame_rate,
            parameters=["-ac", str(orig_audio.channels)],
        )

        return output_filename
