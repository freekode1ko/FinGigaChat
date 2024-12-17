FROM python:3.12


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
COPY --from=root_dir .env /code/

# Run for tests
CMD poetry run python main.py
