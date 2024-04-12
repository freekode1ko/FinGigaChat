FROM ubuntu:22.04

RUN apt-get update
RUN apt-get install python3-dev python3 python3-pip libpq-dev -y
RUN apt-get install ffmpeg -y

COPY . /code
WORKDIR /code

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

RUN poetry install

CMD poetry run python main.py
# ENTRYPOINT ["poetry", "run", "python", "bot_runner.py"]