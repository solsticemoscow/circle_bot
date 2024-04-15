FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

RUN ln -snf /usr/share/zoneinfo/Europe/Moscow /etc/localtime

RUN apt-get update \
  && apt-get install -y gcc \
  && apt-get install -y libpq-dev libgl1 libglib2.0-0 ffmpeg \
  && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/requirements.txt

RUN pip3 install --no-cache-dir --upgrade --default-timeout=10 -r /code/requirements.txt

COPY ./app_bot.py /code/app_bot.py
COPY ./app_task_manager.py /code/app_task_manager.py
COPY ./BOT /code/BOT/


