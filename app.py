import mimetypes

import gradio as gr
import requests

from utils.minio_manager import minio_client

API_URL = "http://localhost:8000/process/"

CATEGORIES = {
    "Сигареты": "cigarettes",
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


def get_selected_categories():
    selected = []

    for main_cat, checkbox in checkboxes_main.items():
        if checkbox.value:  # если основная категория включена
            sub = CATEGORIES[main_cat]
            if isinstance(sub, dict):  # есть подкатегории
                for label, code in sub.items():
                    if checkboxes_sub[main_cat][label].value:
                        selected.append(code)
            else:  # одиночная категория
                selected.append(sub)

    return selected


def process_via_api(file_path, selected_classes, pixelation):
    try:
        key = minio_client.upload_file('uploads', file_path)

        # API
        response = requests.post(
            API_URL,
            json={
                "key": key,
                "black_list": selected_classes,
                "pixelation": pixelation
            }
        )

        if response.status_code != 200:
            return None, None, f"Ошибка: {response.status_code} — {response.text}"

        # Загрузка результата из MinIO
        result_key = response.json()["result_key"]
        result_path = minio_client.download_file('uploads', result_key, 'uploads')

        # Определяем mime тип
        mime_type, _ = mimetypes.guess_type(result_path)
        if mime_type and mime_type.startswith("image"):
            return result_path, None, "✅ Изображение готово"
        elif mime_type and mime_type.startswith("video"):
            return result_path, result_path, "✅ Видео готово"
        else:
            return result_path, None, "✅ Файл готов, но не удалось распознать тип"

    except Exception as e:
        return None, None, f"Ошибка: {str(e)}"


custom_theme = gr.themes.Default(primary_hue="pink")

with gr.Blocks(theme=custom_theme) as demo:
    gr.Markdown("## ACMS Censor")

    with gr.Row():
        with gr.Column():
            input_file = gr.File(label="Загрузите видео, аудио или фото", file_types=["video", "audio", "image"])
        with gr.Column():
            output_view = gr.Video(label="Просмотр", interactive=False)

    with gr.Row():
        pixelation_checkbox = gr.Checkbox(label="Пикселизация (иначе — боксы)", value=True)
        process_button = gr.Button("Обработать")

    checkboxes_main = {}
    checkboxes_sub = {}
    sub_blocks = {}

    # Основные чекбоксы
    with gr.Row():
        for cat in CATEGORIES:
            checkboxes_main[cat] = gr.Checkbox(label=cat)

    # Подкатегории
    for cat, sub in CATEGORIES.items():
        if isinstance(sub, dict) and len(sub) > 1:
            checkboxes_sub[cat] = {}
            with gr.Column(visible=False) as block:
                gr.Markdown(f"Выберите, что нужно цензурировать в «{cat}»:")
                for label in sub:
                    checkboxes_sub[cat][label] = gr.Checkbox(label=label, value=True)
            sub_blocks[cat] = block

    # Выходной файл
    with gr.Row():
        output_file = gr.File(label="Скачайте результат")

    # Функции отображения подблоков
    for cat in sub_blocks:
        checkboxes_main[cat].change(
            lambda checked: gr.update(visible=checked),
            inputs=checkboxes_main[cat],
            outputs=sub_blocks[cat]
        )

    process_button.click(
        fn=lambda file, pixel, *args: process_via_api(file.name, get_selected_categories(), pixel),
        inputs=[input_file, pixelation_checkbox] + list(checkboxes_main.values()) + [cb for group in
                                                                                     checkboxes_sub.values() for cb in
                                                                                     group.values()],
        outputs=[output_file, output_view, gr.Textbox(label="Статус")]
    )

demo.launch()
