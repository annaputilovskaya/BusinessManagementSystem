FROM python:3.11-slim

WORKDIR /app/

RUN pip install --upgrade pip \
    && pip install poetry

COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-root

COPY . /app/