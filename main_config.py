ALL_MODELS: dict[str, list[str]] = {
    "cigarette_detector": ["cigarette"],
    "nude_detector": [
        # "FEMALE_GENITALIA_COVERED",
        # "FACE_FEMALE",
        "BUTTOCKS_EXPOSED",
        "FEMALE_BREAST_EXPOSED",
        "FEMALE_GENITALIA_EXPOSED",
        # "MALE_BREAST_EXPOSED",
        "ANUS_EXPOSED",
        # "FEET_EXPOSED",
        # "BELLY_COVERED",
        # "FEET_COVERED",
        # "ARMPITS_COVERED",
        # "ARMPITS_EXPOSED",
        # "FACE_MALE",
        # "BELLY_EXPOSED",
        "MALE_GENITALIA_EXPOSED",
        # "ANUS_COVERED",
        # "FEMALE_BREAST_COVERED",
        # "BUTTOCKS_COVERED"
    ],
    "extremism_detector": [
        "lgbt",
        "svastika"
    ],
    "bad_words_detector" : ["bad_words"]
}

CATEGORIES = {
    "Сигареты": "cigarette",
    "18+": {
        "Обнажённые ягодицы": "BUTTOCKS_EXPOSED",
        "Обнажённая женская грудь": "FEMALE_BREAST_EXPOSED",
        "Обнажённые женские гениталии": "FEMALE_GENITALIA_EXPOSED",
        "Обнажённая мужская грудь": "MALE_BREAST_EXPOSED",
        "Обнажённый анус": "ANUS_EXPOSED",
        "Обнажённые подмышки": "ARMPITS_EXPOSED",
        "Обнажённый живот": "BELLY_EXPOSED",
        "Обнажённые мужские гениталии": "MALE_GENITALIA_EXPOSED",
    },
    "Экстремизм": {
        "Символика ЛГБТ": "lgbt",
        "Свастика": "svastika",
    },
    "Нецензурная лексика": "bad_words"
}