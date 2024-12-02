FROM python:3.12

RUN pip install alembic environs psycopg2 pandas pathlib

WORKDIR /code
COPY alembic.ini /code/
COPY --from=root_dir .env /code/
COPY --from=root_dir src/global/db/migrations/ /code/migrations/
COPY --from=root_dir src/global/db/models/ /code/models/

RUN ls -la
