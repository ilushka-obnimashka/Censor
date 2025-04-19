import torch
from ultralytics import YOLO

# Configuration parameters for YOLO model training
IMAGE_SIZE = 640  # All images will be resized to this dimension before being fed into the model
BATCH_SIZE = 16    # Batch size options: fixed number (16), auto mode using 60% of GPU memory (-1),
                   # or custom memory fraction (e.g., 0.70)
EPOCHS = 100       # Number of training epochs. Affects training duration and model performance
FREEZE = 10        # Number of layers to freeze (1-24) or specific layer indices as a list ([0, 5, 23])
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # Use GPU if available
DATASET = 'datasets/simvolika/data.yaml'  # Path to YAML dataset configuration file

def main():
    """
    Main function for YOLO model training.
    
    Initializes a pretrained YOLO model (yolo11m.pt) and starts the training process
    with specified parameters. Supports layer freezing for transfer learning.
    
    Official documentation on layer freezing:
    https://docs.ultralytics.com/ru/yolov5/tutorials/transfer_learning_with_frozen_layers/#freeze-backbone
    """
    model = YOLO('temp/yolo11m.pt')  # Load pretrained model
    
    # Start training with specified parameters:
    model.train(
        data=DATASET,
        epochs=EPOCHS,
        batch=BATCH_SIZE,
        imgsz=(IMAGE_SIZE, IMAGE_SIZE),
        device=DEVICE,
        freeze=FREEZE
    )

if __name__ == "__main__":
    main()
