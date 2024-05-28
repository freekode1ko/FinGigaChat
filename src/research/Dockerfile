FROM ubuntu:22.04

RUN apt-get update
RUN apt-get install poppler-utils python3-dev libpq-dev -y
RUN apt-get install python3 python3-pip -y

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN apt-get install -y tzdata

WORKDIR /code

# install packages
COPY ./pyproject.toml /code/pyproject.toml
RUN pip install poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1
RUN poetry install

# Copy project files
COPY . /code

# Run for tests
CMD poetry run python main.py
