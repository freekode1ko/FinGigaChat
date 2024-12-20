FROM ubuntu:22.04

RUN apt-get update -y

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN apt-get install -y tzdata

RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt-get install -y libpq-dev
RUN apt-get install -y gcc
RUN apt-get install -y python3.12-dev
RUN apt-get install -y ffmpeg
RUN apt-get install -y poppler-utils
RUN apt-get install -y wget

RUN wget https://bootstrap.pypa.io/get-pip.py && python3.12 get-pip.py && rm get-pip.py

WORKDIR /code

RUN python3.12 -m pip install poetry
# install pdf_watermark that is a cli util
RUN python3.12 -m pip install pdf-watermark
# install packages
COPY ./pyproject.toml /code/pyproject.toml

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1
RUN poetry install

# Copy project files
COPY . /code
COPY --from=root_dir .env /code/

# Run for tests
CMD poetry run python main.py
# ENTRYPOINT ["poetry", "run", "python", "bot_runner.py"]