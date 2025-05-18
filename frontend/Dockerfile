FROM python:3.12-slim
LABEL authors="ilushka-obnimashka, nikeperl"

WORKDIR /frontend
COPY . .

RUN pip install -r requirements.txt

# Установка cron
RUN apt-get update && apt-get install -y cron

# Добавляем cron-задачу
RUN echo "0,30 * * * * root rm -rf /frontend/results/*" > /etc/cron.d/cleanup_results
RUN chmod 0644 /etc/cron.d/cleanup_results
RUN crontab /etc/cron.d/cleanup_results

# Запускаем cron и приложение вместе (cron в фоне)
CMD cron && python gradio_frontend.py