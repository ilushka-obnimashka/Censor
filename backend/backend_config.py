ALL_MODELS: dict[str, list[str]] = {
    "cigarette_detector": ["cigarette"],
    "nude_detector": [
        # "FEMALE_GENITALIA_COVERED",
        "FACE_FEMALE",
        "BUTTOCKS_EXPOSED",
        "FEMALE_BREAST_EXPOSED",
        "FEMALE_GENITALIA_EXPOSED",
        "MALE_BREAST_EXPOSED",
        "ANUS_EXPOSED",
        # "FEET_EXPOSED",
        # "BELLY_COVERED",
        # "FEET_COVERED",
        # "ARMPITS_COVERED",
        "ARMPITS_EXPOSED",
        "FACE_MALE",
        "BELLY_EXPOSED",
        "MALE_GENITALIA_EXPOSED",
        # "ANUS_COVERED",
        # "FEMALE_BREAST_COVERED",
        # "BUTTOCKS_COVERED"
    ],
    "extremism_detector": [
        "lgbt",
        "svastika"
    ],
    "bad_words_detector": ["bad_words"]
}
