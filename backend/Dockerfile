FROM nvidia/cuda:12.9.0-base-ubuntu24.04
LABEL authors="ilushka-obnimashka, nikeperl"

# Установка Python 3.12 и pip
RUN apt-get update && apt-get install -y \
    python3.12 curl && \
    python3.12 -m ensurepip && \
    python3.12 -m pip install --upgrade pip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /backend
COPY . .

# Обновляем pip, устанавливаем зависимости
RUN python3.12 -m pip install --upgrade pip

# Установка PyTorch с поддержкой CUDA 12.9 и зависимостей из requirements.txt
RUN python3.12 -m pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
RUN python3.12 -m pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3.12", "main_API.py"]