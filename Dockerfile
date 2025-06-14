FROM python:3.10

RUN apt-get update \
 && apt-get install -y --no-install-recommends postgresql-client \
 && rm -rf /var/lib/apt/lists/*

RUN useradd -m docker_app

WORKDIR /team_social_network

COPY --chown=docker_app:docker_app pyproject.toml poetry.lock ./

USER root
RUN apt-get update && apt-get install -y netcat-openbsd
RUN pip install --no-cache-dir poetry==2.1.2

RUN poetry config virtualenvs.in-project true \
 && poetry install --no-root

ENV PATH="/team_social_network/.venv/bin:${PATH}"

RUN chown -R docker_app:docker_app /team_social_network
USER docker_app
COPY --chown=docker_app:docker_app . .

CMD ["/team_social_network/.venv/bin/python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3456"]

