import torch
import cv2
from ultralytics import YOLO

IMAGE_SIZE = 640 # All images are resized to this dimension before being fed into the model
BATCH_SIZE = 16 # Batch size, with three modes: set as an integer (16), auto mode for 60% GPU memory utilization (-1), or auto mode with specified utilization fraction (0.70).
EPOCHS = 100 # Adjusting this value can affect training duration and model performance
FREEZE = 10 # Freezes the first N  layers of the model (1 - 24) or specified layers by index, if you use list ([0, 5, 23])
isTRAIN = False
DATASET = 'cigarette_dataset/data.yaml' # Path to your *.yaml file for dataset
video_path = 'testvideo.mp4'

def is_cuda_available():
    """
    Checks Cuda availability and determines the video card name.
    :return the device for calculations.
    """
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        print(f"CUDA доступна. Используется видеокарта: {gpu_name}")
    else:
        print("CUDA не доступна. Вычисления будут производиться на CPU.")

    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

def cv_output(cap, results):
    frame_index = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        annotated_frame = results[frame_index].plot()
        cv2.imshow("YOLO Detection", annotated_frame)
        frame_index += 1

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

def pixelation(cap, predicts):
    # Получаем параметры видео
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Настройка VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Кодек MP4
    out = cv2.VideoWriter('result.mp4', fourcc, fps, (frame_width, frame_height))

    frame_index = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        for box in predicts[frame_index].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            x1 -= 5
            y1 -= 5
            x1 += 5
            y1 += 5

            roi_width = x2 - x1
            roi_height = y2 - y1

            new_w = int(3 * round(roi_width / min(roi_width, roi_height)))
            new_h = int(3 * round(roi_height / min(roi_width, roi_height)))

            # Пикселизация
            roi = frame[y1:y2, x1:x2]
            roi = cv2.resize(roi, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            roi = cv2.resize(roi, (roi_width, roi_height), interpolation=cv2.INTER_NEAREST)
            frame[y1:y2, x1:x2] = roi

        # Записываем обработанный кадр в выходное видео
        out.write(frame)
        frame_index += 1

    cap.release()
    out.release()
    print(f"Применена визуальная цензура")

    return cv2.VideoCapture('result.mp4')

def main():
    """
    Main function
    :return:
    """
    if isTRAIN:
        model = YOLO('yolo11m.pt')
        # Information from official source https://docs.ultralytics.com/ru/yolov5/tutorials/transfer_learning_with_frozen_layers/#freeze-backbone

        results = model.train(data=DATASET, epochs=EPOCHS, imgsz=IMAGE_SIZE, device=is_cuda_available(), freeze=FREEZE)
    else:
        model = YOLO('runs/detect/train4/weights/best.pt')

    results = model(video_path)
    cap = cv2.VideoCapture(video_path)
    cap2 = pixelation(cap, results)
    cv_output(cap2, results)



if __name__ == "__main__":
    main()