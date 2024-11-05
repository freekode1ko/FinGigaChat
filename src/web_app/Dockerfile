# Сборка фронтенда
FROM node:18-alpine AS frontend-build
WORKDIR /code/frontend
COPY ./react_frontend/package.json ./react_frontend/package-lock.json ./
RUN npm install
COPY ./react_frontend .
RUN npm run build

# Установка зависимостей для бэкенда
FROM python:3.10-slim AS backend-build
WORKDIR /code
COPY ./pyproject.toml .
RUN pip install --no-cache-dir poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1
RUN poetry install --no-root --only main

# Сборка финального образа
FROM python:3.10-slim AS final
WORKDIR /code
COPY --from=frontend-build /code/frontend/dist/index.html /code/frontend/templates/index.html
COPY --from=frontend-build /code/frontend/dist/static /code/frontend/static
COPY --from=backend-build /code/.venv /code/.venv
COPY . .
ENV PATH="/code/.venv/bin:$PATH"
