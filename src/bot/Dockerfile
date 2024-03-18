FROM python:3.10

COPY . /code
WORKDIR /code

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

RUN poetry install

CMD poetry run python main.py
# ENTRYPOINT ["poetry", "run", "python", "bot_runner.py"]