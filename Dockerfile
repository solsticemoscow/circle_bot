FROM python:3.11-slim

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN ln -snf /usr/share/zoneinfo/Europe/Moscow /etc/localtime

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y gcc \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev libgl1 libglib2.0-0 \
  # cleaning up unused files
  && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/requirements.txt

RUN pip3 install --no-cache-dir --upgrade --default-timeout=10 -r /code/requirements.txt


COPY ./BOT/ /code/BOT
COPY ./BOT/data/textures /code/BOT/DATA/textures
COPY ./BOT/data/own_texture.PNG /code/BOT/DATA/own_texture.PNG
COPY ./BOT/data/texture_help.PNG /code/BOT/DATA/texture_help.PNG
COPY ./BOT/data/textures_choose.PNG /code/BOT/DATA/textures_choose.PNG
COPY ./BOT/data/video_round_bot.png /code/BOT/DATA/video_round_bot.png
COPY ./BOT/data/help_buy_sub.gif /code/BOT/DATA/help_buy_sub.gif