FROM python:3.11.0-slim as requirements-stage

WORKDIR /tmp
RUN pip install poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11.0-slim

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY ./src/dynamic_models_api /code
WORKDIR /code
ENV PYTHONPATH=/code
