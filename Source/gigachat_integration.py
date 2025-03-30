from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat import GigaChat


def setup_gigachat_client(auth_token: str) -> GigaChat:
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


def prepare_profanity_detection_prompt(timestamps_words: list[dict[str, float]]) -> str:
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


def detect_profanity(client: GigaChat, timestamps_words: list[dict[str, float]]) -> list[dict[str, float]]:
    """
    Detects profanity words using the GigaChat client.

    :param client: The configured GigaChat client instance.
    :param timestamps_words: A list of dictionaries containing word information and their timestamps.
    :return: A list of dictionaries with profanity words and their timestamps.
             Returns `None` if an error occurs during the request.
    """
    prompt = prepare_profanity_detection_prompt(timestamps_words)

    print(prompt)

    messages = [
        SystemMessage(content="Ты помощник, который точно определяет матерные слова."),
        HumanMessage(content=prompt)
    ]

    try:
        response = client.invoke(messages)
        return response.content[7:-3]
    except Exception as e:
        print(f"Error during request: {e}")
        return None
