FROM python:3.12-slim
LABEL authors="ilushka-obnimashka, nikeperl"

WORKDIR /backend
COPY backend/ .

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main_API.py"]