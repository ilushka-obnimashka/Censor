import torch
from ultralytics import YOLO


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

def main():
    """
    Main function
    :return:
    """
    model = YOLO('yolo11m.pt')
    # Information from official source https://docs.ultralytics.com/ru/yolov5/tutorials/transfer_learning_with_frozen_layers/#freeze-backbone
    # The model is based on levels 0-9

    freeze = 10  # Changing the number in the range from 1 to 24 will freeze the layers with 'model.0.' - 'model.1.'/ 'model.23.'
    freeze = [f"model.{x}." for x in range(freeze)]  # layers to freeze
    for k, v in model.named_parameters():
        v.requires_grad = True  # train all layers
        if any(x in k for x in freeze):
            v.requires_grad = False

    # Important: Заполнить data=''
    results = model.train(data='', epochs=100, imgsz=640, device=is_cuda_available())

if __name__ == "__main__":
    main()