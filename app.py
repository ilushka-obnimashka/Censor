import gradio as gr

CATEGORIES = {
    # Основные категории
    "Сигареты": "cigarettes",
    "18+": {
        "Обнажённые ягодицы": "BUTTOCKS_EXPOSED",
        "Обнажённая женская грудь": "FEMALE_BREAST_EXPOSED",
        "Обнажённые женские гениталии": "FEMALE_GENITALIA_EXPOSED",
        "Обнажённая мужская грудь": "MALE_BREAST_EXPOSED",
        "Обнажённый анус": "ANUS_EXPOSED",
        "Обнажённые ступни": "FEET_EXPOSED",
        "Обнажённые подмышки": "ARMPITS_EXPOSED",
        "Обнажённый живот": "BELLY_EXPOSED",
        "Обнажённые мужские гениталии": "MALE_GENITALIA_EXPOSED",
    },
    "Экстремизм": {
        "Символика ЛГБТ": "lgbt",
        "Свастика": "svastika",
    },
    "Нецензурная лексика": "profanity"
}


def process_file(input_file, сигареты, is_18_plus, ягодицы, женская_грудь, женские_гениталии, мужская_грудь, анус,
                 ступни, подмышки, живот, мужские_гениталии, экстремизм, лгбт, свастика, нецензурная_лексика):
    # Здесь будет логика обработки
    # Пока просто возвращаем тот же файл
    return input_file


with gr.Blocks() as demo:
    gr.Markdown("## Обработка видео/аудио/фото с цензурой")

    with gr.Row():
        input_file = gr.File(label="Загрузите видео, аудио или фото", file_types=["video", "audio", "image"])

    with gr.Row():
        сигареты = gr.Checkbox(label="Сигареты", value=True)
        is_18_plus = gr.Checkbox(label="18+", value=False)
        экстремизм = gr.Checkbox(label="Экстремизм", value=False)
        нецензурная_лексика = gr.Checkbox(label="Нецензурная лексика", value=True)

    # Блок для 18+
    with gr.Column(visible=False) as plus_18_options:
        gr.Markdown("**Выберите, что нужно цензурировать в 18+:**")
        ягодицы = gr.Checkbox(label="Обнажённые ягодицы", value=True)
        женская_грудь = gr.Checkbox(label="Обнажённая женская грудь", value=True)
        женские_гениталии = gr.Checkbox(label="Обнажённые женские гениталии", value=True)
        мужская_грудь = gr.Checkbox(label="Обнажённая мужская грудь", value=True)
        анус = gr.Checkbox(label="Обнажённый анус", value=True)
        ступни = gr.Checkbox(label="Обнажённые ступни", value=False)
        подмышки = gr.Checkbox(label="Обнажённые подмышки", value=False)
        живот = gr.Checkbox(label="Обнажённый живот", value=False)
        мужские_гениталии = gr.Checkbox(label="Обнажённые мужские гениталии", value=True)

    # Блок для экстремизма
    with gr.Column(visible=False) as extremism_options:
        gr.Markdown("**Выберите, что нужно цензурировать в экстремизме:**")
        лгбт = gr.Checkbox(label="Символика ЛГБТ", value=False)
        свастика = gr.Checkbox(label="Свастика", value=True)

    with gr.Row():
        process_button = gr.Button("Обработать")

    with gr.Row():
        output_file = gr.File(label="Скачайте результат")


    # Функция отображения 18+ подпунктов
    def toggle_18_plus(is_checked):
        return gr.update(visible=is_checked)


    # Функция отображения экстремизма подпунктов
    def toggle_extremism(is_checked):
        return gr.update(visible=is_checked)


    # Привязываем логику показа блоков
    is_18_plus.change(
        toggle_18_plus,
        inputs=[is_18_plus],
        outputs=[plus_18_options]
    )

    экстремизм.change(
        toggle_extremism,
        inputs=[экстремизм],
        outputs=[extremism_options]
    )

    process_button.click(
        process_file,
        inputs=[
            input_file, сигареты, is_18_plus,
            ягодицы, женская_грудь, женские_гениталии, мужская_грудь, анус, ступни, подмышки, живот, мужские_гениталии,
            экстремизм, лгбт, свастика,
            нецензурная_лексика
        ],
        outputs=[output_file]
    )

demo.launch()
