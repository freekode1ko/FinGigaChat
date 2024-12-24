FROM ubuntu:22.04

RUN apt-get update -y

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN apt-get install -y tzdata

RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa


RUN apt-get install -y wget
RUN apt-get install -y python3.12-dev
RUN wget https://bootstrap.pypa.io/get-pip.py && python3.12 get-pip.py && rm get-pip.py
RUN apt-get install -y libpq-dev
RUN apt-get install -y gcc

RUN apt-get install -y poppler-utils

WORKDIR /code

# install packages
COPY ./pyproject.toml /code/pyproject.toml
RUN python3.12 -m pip install poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1
RUN python3.12 -m poetry install

# Copy project files
COPY . /code
COPY --from=root_dir .env /code/

# Run for tests
CMD poetry run python main.py
