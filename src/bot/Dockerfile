FROM ubuntu:22.04

RUN apt-get update -y
RUN apt-get install poppler-utils python3-setuptools python3-dev libpq-dev -y
RUN apt-get install python3 python3-pip -y
RUN apt-get install ffmpeg -y

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN apt-get install -y tzdata

WORKDIR /code

# install packages
COPY ./pyproject.toml /code/pyproject.toml
RUN pip install poetry

# install pdf_watermark that is a cli util
RUN pip install pdf-watermark

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1
RUN poetry install

# Copy project files
COPY . /code

# Run for tests
CMD poetry run python main.py
# ENTRYPOINT ["poetry", "run", "python", "bot_runner.py"]
