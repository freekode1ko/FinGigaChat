FROM node:18 AS frontend-build

WORKDIR /code

COPY ./react_frontend/package.json ./react_frontend/package-lock.json /code/react_frontend/

RUN cd /code/react_frontend && npm install

COPY ./react_frontend /code/react_frontend
RUN cd /code/react_frontend && npm run build


FROM python:3.10

WORKDIR /code

# install packages
COPY ./pyproject.toml /code/pyproject.toml
RUN pip install poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1
RUN poetry install

COPY --from=frontend-build /code/react_frontend/dist/index.html /code/frontend/templates/index.html
COPY --from=frontend-build /code/react_frontend/dist/static/js/main.js /code/frontend/static/js/main.js
COPY --from=frontend-build /code/react_frontend/dist/static/css/main.css /code/frontend/static/css/main.css

COPY . /code
