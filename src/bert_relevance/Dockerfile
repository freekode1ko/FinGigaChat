FROM python:3.12

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

WORKDIR /code

COPY ./pyproject.toml /code/pyproject.toml

RUN poetry install

COPY . /code
