FROM python:3.10-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc libpq-dev postgresql-client \
 && rm -rf /var/lib/apt/lists/*

RUN useradd -m docker_app

WORKDIR /team_social_network

COPY --chown=docker_app:docker_app pyproject.toml poetry.lock ./

USER root
RUN pip install --no-cache-dir poetry==2.1.2

RUN poetry config virtualenvs.in-project true \
 && poetry install --no-root --only main

ENV PATH="/team_social_network/.venv/bin:${PATH}"

COPY --chown=docker_app:docker_app . .

RUN chown -R docker_app:docker_app /team_social_network
USER docker_app

CMD ["/team_social_network/.venv/bin/python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3456"]

