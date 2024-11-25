FROM python:3.12

WORKDIR /code

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

COPY ./pyproject.toml /code/pyproject.toml
RUN poetry install

COPY --from=root_dir .env /code/

COPY . /code
