FROM python:3.12-slim
LABEL authors="ilushka-obnimashka, nikeperl"

WORKDIR /backend
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

ENTRYPOINT ["python", "main_API.py"]