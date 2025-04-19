import torch
from ultralytics import YOLO

IMAGE_SIZE = 640 # All images are resized to this dimension before being fed into the model
BATCH_SIZE = 16 # Batch size, with three modes: set as an integer (16), auto mode for 60% GPU memory utilization (-1), or auto mode with specified utilization fraction (0.70).
EPOCHS = 100 # Adjusting this value can affect training duration and model performance
FREEZE = 10 # Freezes the first N  layers of the model (1 - 24) or specified layers by index, if you use list ([0, 5, 23])
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
DATASET = 'datasets/' # Path to your *.yaml file for dataset

def main():
    model = YOLO('temp/yolo11m.pt')
    # Information from official source https://docs.ultralytics.com/ru/yolov5/tutorials/transfer_learning_with_frozen_layers/#freeze-backbone
    model.train(data=DATASET, epochs=EPOCHS, batch=BATCH_SIZE, imgsz=(IMAGE_SIZE, IMAGE_SIZE), device=DEVICE, freeze=FREEZE)

if __name__ == "__main__":
    main()