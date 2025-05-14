import mimetypes
import os
import traceback

import gradio as gr
import requests

from utils import minio_client
from frontend_config import CATEGORIES

API_URL = os.getenv("API_URL")


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
        print(selected_classes)

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
            return None, f"Ошибка: {response.status_code} — {response.text}"

        # Загрузка результата из MinIO
        result_key = response.json()["result_key"]
        result_path = minio_client.download_file('uploads', result_key, 'result')

        # Удаляем из minio

        return gr.update(value=result_path, visible=True), "Файл обработан!"

    except Exception as e:
        raise f"Ошибка: {traceback.format_exc()}"


def update_preview(file_path):
    try:
        if file_path is None:
            return (
                gr.update(visible=False),  # output_file
                gr.update(value=None, visible=False),  # video
                gr.update(value=None, visible=False),  # image
                gr.update(value=None, visible=False),  # audio
                gr.update(value="wait...", visible=True)
            )

        show_video = gr.update(value=None, visible=False)
        show_image = gr.update(value=None, visible=False)
        show_audio = gr.update(value=None, visible=False)

        # Определяем mime тип
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            if mime_type.startswith("video"):
                show_video = gr.update(value=file_path, visible=True)
            elif mime_type.startswith("image"):
                show_image = gr.update(value=file_path, visible=True)
            elif mime_type.startswith("audio"):
                show_audio = gr.update(value=file_path, visible=True)
        return file_path, show_video, show_image, show_audio, gr.update(visible=False)

    except Exception as e:
        print(f"update_preview: {traceback.format_exc()}")
        return None, None, None, None, None


custom_theme = gr.themes.Default(primary_hue="pink")

with gr.Blocks(theme=custom_theme) as demo:
    gr.Markdown("## ACMS Censor <sub>v1.0.0-alpha</sub>")

    with gr.Row(equal_height=True):
        with gr.Column():
            input_file = gr.File(label="Загрузите видео, аудио или фото", file_types=["video", "audio", "image"])
            output_file = gr.File(label="Скачайте результат", visible=False)
        with gr.Column():
            output_view_video = gr.Video(label="Просмотр", visible=False)
            output_view_image = gr.Image(label="Просмотр", visible=False)
            output_view_audio = gr.Audio(label="Прослушивание", visible=False)
            status_text = gr.Textbox(label="Статус", value="wait...", visible=True)

    with gr.Row(equal_height=True):
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

    # Функции отображения подблоков
    for cat in sub_blocks:
        checkboxes_main[cat].change(
            lambda checked: gr.update(visible=checked),
            inputs=checkboxes_main[cat],
            outputs=sub_blocks[cat]
        )

    process_button.click(
        fn=lambda file, pixel, *args: process_via_api(file.name, get_selected_categories(), pixel),
        inputs=[input_file, pixelation_checkbox] +
               list(checkboxes_main.values()) +
               [cb for group in checkboxes_sub.values() for cb in group.values()],
        outputs=[output_file, status_text]
    )

    output_file.change(
        fn=update_preview,
        inputs=output_file,
        outputs=[
            output_file,
            output_view_video,
            output_view_image,
            output_view_audio,
            status_text
        ]
    )

demo.launch()
