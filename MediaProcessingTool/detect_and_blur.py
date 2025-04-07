import cv2
import click
import censore_models
import random
import time
import mimetypes

all_models = {
    'cigarette': ["cigarette"],
    'nude': [
        "FEMALE_GENITALIA_COVERED",
        "FACE_FEMALE",
        "BUTTOCKS_EXPOSED",
        "FEMALE_BREAST_EXPOSED",
        "FEMALE_GENITALIA_EXPOSED",
        "MALE_BREAST_EXPOSED",
        "ANUS_EXPOSED",
        "FEET_EXPOSED",
        "BELLY_COVERED",
        "FEET_COVERED",
        "ARMPITS_COVERED",
        "ARMPITS_EXPOSED",
        "FACE_MALE",
        "BELLY_EXPOSED",
        "MALE_GENITALIA_EXPOSED",
        "ANUS_COVERED",
        "FEMALE_BREAST_COVERED",
        "BUTTOCKS_COVERED",
    ],
}

def get_color(class_name):
    """Генерирует цвет на основе класса."""
    random.seed(class_name)  # устанавливаем seed по строке
    return (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )

def draw_box(img, x1, y1, x2, y2, label):
    """Рисует рамку вокруг детектированного объектов."""
    color = get_color(label)

    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
    cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

def pixelation_box(img, x1, y1, x2, y2):
    """Пикселизирует область, где была детекция."""
    h, w = img.shape[:2]
    x1 = max(0, x1 - 5)
    y1 = max(0, y1 - 5)
    x2 = min(w, x2 + 5)
    y2 = min(h, y2 + 5)

    roi = img[y1:y2, x1:x2]
    if roi.size == 0:
        return

    roi_h, roi_w = roi.shape[:2]

    new_w = int(3 * round(roi_w / min(roi_w, roi_h)))
    new_h = int(3 * round(roi_h / min(roi_w, roi_h)))

    # Пикселизация
    roi = cv2.resize(roi, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    roi = cv2.resize(roi, (roi_w, roi_h), interpolation=cv2.INTER_NEAREST)
    img[y1:y2, x1:x2] = roi

def model(img, models_to_apply):
    results = []

    if 'cigarette' in models_to_apply:
        results.extend(censore_models.cigarette(img))
    if 'nude' in models_to_apply:
        results.extend(censore_models.nude(img))
    if 'alcohol' in models_to_apply:
        results.extend(censore_models.alcohol(img))
    if 'extremism' in models_to_apply:
        results.extend(censore_models.extremism(img))

    return results


def process_image(input_path, black_list, models_to_apply, pixelation=True, output_path=None, show=False):
    """Прогоняет изображение через модель, пикселизирует детектированные области и сохраняет результат."""
    image = cv2.imread(input_path)
    results = model(image, models_to_apply)

    for result in results:
        class_name = result['class']
        x1, y1, x2, y2 = result['box']
        if class_name in black_list:
            if pixelation:
                pixelation_box(image, x1, y1, x2, y2)
            else:
                draw_box(image, x1, y1, x2, y2, class_name)

    if output_path:
        cv2.imwrite(output_path, image)

    if show:
        cv2.imshow('YOLO Image', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def process_video(input_path, black_list, models_to_apply, pixelation=True, output_path=None, show=False):
    """Прогоняет видео через модель, пикселизирует детектированные области и сохраняет результат."""
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frames = []

    tracker_type = "CSRT"  # Можно попробовать KCF, MOSSE и другие
    trackers = cv2.legacy.MultiTracker_create()
    tracked_class_names = []  # Сохраняем названия классов
    frame_count = 0
    tracking_interval = fps // 2

    while cap.isOpened():
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % tracking_interval == 0: #
            results = model(frame, models_to_apply)
            trackers = cv2.legacy.MultiTracker_create()

            tracked_class_names.clear()  # Сброс названий классов

            for result in results:
                class_name = result['class']
                x1, y1, x2, y2 = result['box']
                if class_name in black_list:
                    if pixelation:
                        pixelation_box(frame, x1, y1, x2, y2)
                    else:
                        draw_box(frame, x1, y1, x2, y2, class_name)

                    # Создание и добавление нового трекера
                    tracker = cv2.legacy.TrackerCSRT_create()
                    trackers.add(tracker, frame, (x1, y1, x2 - x1, y2 - y1))
                    tracked_class_names.append(class_name)  # сохраняем имя класса

        else:
            # Используем трекер между детекциями
            success, boxes = trackers.update(frame)
            for i, newbox in enumerate(boxes):
                class_name = tracked_class_names[i] if i < len(tracked_class_names) else "Tracked"
                x, y, w, h = map(int, newbox)
                if class_name in black_list:
                    if pixelation:
                        pixelation_box(frame, x, y, x + w, y + h)
                    else:
                        draw_box(frame, x, y, x + w, y + h, class_name)

        frame_count += 1 # счет

        if show:
            cv2.imshow('YOLO Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        frames.append(frame)
        print(f'Время кадра: {time.time() - start_time}')


    cap.release()
    cv2.destroyAllWindows()
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        for frame in frames:
            out.write(frame)
        out.release()


def process_file(input_path, black_list, pixelation=True, output_path=None, show=False):
    """Автоматически выберает видео или изображение и выбирает модели которые надо использовать."""
    mime_type, _ = mimetypes.guess_type(input_path)

    if mime_type is None:
        print("Неизвестный формат файла")
        return

    if output_path == None and show == False:
        print("Не указан путь вывода")
        return

    models_to_apply = []

    # Проходим по маппингу и ищем, какие классы подходят для моделей
    for model, model_classes in all_models.items():
        if any(cls in black_list for cls in model_classes):
            models_to_apply.append(model)

    if mime_type.startswith('image'):
        process_image(input_path, black_list, models_to_apply, pixelation, output_path, show)
    elif mime_type.startswith('video'):
        process_video(input_path, black_list, models_to_apply, pixelation, output_path, show)
    else:
        print("Файл не является изображением или видео")


@click.group()
def cli():
    pass

@cli.command(help="Обработка медиа.")
@click.argument("input_path", type=click.Path(exists=True))
@click.option("--black-list", "-b", multiple=True, required=True, help="Список классов для блюра (например: --black-list cigarette --black-list MALE_GENITALIA_EXPOSED)")
@click.option("--pixelation/--no-pixelation", default=True, help="Пикселизация или контур.")
@click.option("--output-path", "-o", type=click.Path(), help="Путь к выходному файлу.")
@click.option("--show", is_flag=True, help="Показать в реальном времени (только для разработчиков).", hidden=True)
def parse(input_path, black_list, pixelation, output_path, show):
    process_file(input_path, list(black_list), pixelation=pixelation, output_path=output_path, show=show)

if __name__ == "__main__":
    cli()