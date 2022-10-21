
# BASE IMAGE

FROM python:3.10-slim-bullseye AS base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"


# BUILDER

FROM base AS builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.2.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN buildDeps="build-essential" \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
        curl $buildDeps \
    && rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    chmod a+x /opt/poetry/bin/poetry

WORKDIR "$PYSETUP_PATH"
COPY ./poetry.lock* ./pyproject.toml ./

RUN poetry run pip install --upgrade pip setuptools wheel && \
    poetry install --no-root --without dev && \
    poetry run pip install "uvicorn[standard]>=0.18,<1.0" "gunicorn>=20.1,<21.0"
COPY . .
RUN poetry build && \
    poetry run pip install dist/*.whl


# PROD SERVER APP IMAGE

FROM base AS prod

ENV FASTAPI_ENV=production

COPY --from=builder "$VENV_PATH" "$VENV_PATH"

COPY ./gunicorn_conf.py /gunicorn_conf.py
COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

RUN groupadd -g 1337 textrig && \
    useradd -m -u 1337 -g textrig textrig

USER textrig

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["textrig.app:app", "--config", "/gunicorn_conf.py"]
