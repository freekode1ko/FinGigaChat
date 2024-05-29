FROM python

WORKDIR /code

COPY ./pyproject.toml /code/pyproject.toml

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

RUN poetry install

COPY . /code
