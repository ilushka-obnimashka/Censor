import json
import math
import os.path
import wave

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat import GigaChat
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer

from .base_detector import *

from utils.video_audio_tools import audio_format_transcoder
from utils.temp_file_manager import TempFilesManager

class BadWordsDetector(BaseDetector):
    def __init__(self, device: str = 'cuda'):
        super().__init__('models/vosk-model-small-ru-0.22', device)
        self.model_ = Model(self.model_path)
        self.recognizer_ = KaldiRecognizer(self.model_, 16000)
        self.giga_client_ = self.setup_gigachat_client(os.environ.get("GIGA_CHAT_KEY"))

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

        return self.censor_audio(result, media, "models/censor_sound.mp3")

    def get_word_timestamps_vosk(self, audio_path: str) -> list[dict[str, str | float]]:
        """
        Removes temporary marks of words from the audio file using the VOSK model.

        :param audio_path: The path to the audio file for processing.
        :return: A list of dictionaries containing information about words and their time tags.
        """
        try:
            correct_format_audio = audio_format_transcoder(audio_path)
        except RuntimeError as e:
            raise RuntimeError(f"in get_word_timestamps_vosk(BadWordsDetector) Could not convert audio file: {str(e)}") from e

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

        #print(prompt)

        messages = [
            SystemMessage(content="Ты помощник, который точно определяет матерные слова."),
            HumanMessage(content=prompt)
        ]

        try:
            response = self.giga_client_.invoke(messages)
            print(response.content)
            return response.content

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
        orig_name, orig_format  = os.path.splitext(os.path.basename(orig_audio_path))
        output_filename = TempFilesManager().create_temp_file(f"{orig_name}_censor{orig_format}")

        orig_audio = AudioSegment.from_file(orig_audio_path)

        if not profanity_timestamps or not profanity_timestamps["profanity_timestamps"]:  # Проверяем, что список пуст
            orig_audio.export(output_filename, format=orig_format[1:])
            return output_filename

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

        censored_audio.export(output_filename, format=orig_format[1:])

        return output_filename




