FROM ubuntu:22.04

RUN apt-get update -y
RUN apt-get install python3-setuptools python3-dev libpq-dev -y
RUN apt-get install python3 python3-pip -y
RUN apt-get install ffmpeg -y

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN apt-get install -y tzdata

COPY . /code
WORKDIR /code

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

RUN poetry install

CMD poetry run python main.py
# ENTRYPOINT ["poetry", "run", "python", "bot_runner.py"]
