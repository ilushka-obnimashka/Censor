FROM python:3.12-slim
LABEL authors="ilushka-obnimashka, nikeperl"

WORKDIR /frontend
COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "gradio_frontend.py"]