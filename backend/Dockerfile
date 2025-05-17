FROM nvidia/cuda:12.9.0-base-ubuntu24.04
LABEL authors="ilushka-obnimashka, nikeperl"

# Установка Python 3 pip OpenGL ffmpeg
RUN apt-get update && apt-get install -y python3 python3-pip libgl1 ffmpeg

WORKDIR /backend
COPY . .

# Обновляем pip
RUN python3 -m pip install --upgrade pip --break-system-packages --ignore-installed

# Установка PyTorch с поддержкой CUDA 12.9 и зависимостей из requirements.txt
RUN python3 -m pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128 --break-system-packages
RUN python3 -m pip install --no-cache-dir -r requirements.txt --break-system-packages

ENTRYPOINT ["python3", "main_API.py"]