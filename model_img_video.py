import torch
import cv2
import numpy as np
from ultralytics import YOLO
from patched_yolo_infer import MakeCropsDetectThem, CombineDetections, visualize_results, auto_calculate_crop_values

IMAGE_SIZE = 640 # All images are resized to this dimension before being fed into the model
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL = YOLO('runs/detect/train4/weights/best.pt')

def get_color(class_id):
    """Генерирует цвет на основе ID класса."""
    np.random.seed(class_id)
    return tuple(np.random.randint(0, 255, 3).tolist())

def draw_box(img, x1, y1, x2, y2, class_id, label):
    """Рисует рамку вокруг детектированного объектов."""
    color = get_color(class_id)

    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
    cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

def pixelation_box(img, x1, y1, x2, y2):
    """Пикселизирует область, где была детекция."""
    x1 -= 5
    y1 -= 5
    x1 += 5
    y1 += 5

    roi_width = x2 - x1
    roi_height = y2 - y1

    new_w = int(3 * round(roi_width / min(roi_width, roi_height)))
    new_h = int(3 * round(roi_height / min(roi_width, roi_height)))

    # Пикселизация
    roi = img[y1:y2, x1:x2]
    roi = cv2.resize(roi, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    roi = cv2.resize(roi, (roi_width, roi_height), interpolation=cv2.INTER_NEAREST)
    img[y1:y2, x1:x2] = roi


def process_image(image_path, output_path=None, show=False):
    """Прогоняет изображение через модель, пикселизирует детектированные области и сохраняет результат."""
    image = cv2.imread(image_path)
    results = MODEL(image, imgsz=(IMAGE_SIZE, IMAGE_SIZE))

    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        class_id = int(box.cls[0])
        draw_box(image, x1, y1, x2, y2, class_id, results[0].names[class_id])

    if output_path:
        cv2.imwrite(output_path, image)

    if show:
        cv2.imshow('YOLO Image', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def process_video(video_path, output_path=None, show=False):
    """Прогоняет видео через модель, пикселизирует детектированные области и сохраняет результат."""
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frames = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        results = MODEL(frame, imgsz=(IMAGE_SIZE, IMAGE_SIZE))

        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            class_id = int(box.cls[0])
            draw_box(frame, x1, y1, x2, y2, class_id, results[0].names[class_id])

        # annotated_frame = results[0].plot() # Обводка
        frames.append(frame)

        if show:
            cv2.imshow('YOLO Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        for frame in frames:
            out.write(frame)
        out.release()



def patched_image(source):
    """Прогоняет изображение через модель с разбиением и сохраняет результат."""
    # Calculate the optimal crop size and overlap for an image
    shape_x, shape_y, overlap_x, overlap_y = auto_calculate_crop_values(
        image=source, mode="network_based", model=MODEL
    )

    if (shape_x < IMAGE_SIZE):
        shape_x = IMAGE_SIZE
    if (shape_y < IMAGE_SIZE):
        shape_y = IMAGE_SIZE

    element_crops = MakeCropsDetectThem(
        image=source,
        model=MODEL,
        segment=False,
        shape_x=shape_x,
        shape_y=shape_y,
        overlap_x=overlap_x,
        overlap_y=overlap_y,
        conf=0.5,
        iou=0.7,
    )
    # Assuming result is an instance of the CombineDetections class
    return CombineDetections(element_crops, nms_threshold=0.25)

def process_patched_video(video_path, output_path=None, show=False):
    """Прогоняет видео с разбиением на патчи через модель,
     пикселизирует детектированные области и сохраняет результат."""
    cap = cv2.VideoCapture(video_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frames = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        result = patched_image(frame)

        i = 0
        for box in result.filtered_boxes:
            x1, y1, x2, y2 = map(int, box)
            class_id = int(result.filtered_classes_id[i])
            draw_box(frame, x1, y1, x2, y2, class_id, result.filtered_classes_names[i])
            i+=1

        # annotated_frame = results[0].plot() # Обводка
        frames.append(frame)

        if show:
            cv2.imshow('YOLO Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        for frame in frames:
            out.write(frame)
        out.release()




def main():
    # process_image("1.webp", show=True)
    process_video('testvideo.mp4', show=True)

if __name__ == "__main__":
    main()