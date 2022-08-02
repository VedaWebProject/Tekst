FROM python:3.10-slim-bullseye AS base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"



FROM base AS builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.1.14

RUN buildDeps="build-essential" \
    && apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
    && apt-get install -y --no-install-recommends $buildDeps \
    && rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python && \
    chmod a+x /opt/poetry/bin/poetry

WORKDIR "$PYSETUP_PATH"
COPY ./poetry.lock* ./pyproject.toml ./
RUN poetry run pip install --upgrade pip setuptools wheel && \
    poetry install --no-dev --no-root && \
    poetry run pip install "uvicorn[standard]>=0.18,<1.0" "gunicorn>=20.1,<21.0"

COPY . .
RUN poetry build && \
    poetry run pip install dist/*.whl



FROM base AS prod

ENV FASTAPI_ENV=production

COPY --from=builder "$VENV_PATH" "$VENV_PATH"

COPY ./docker/gunicorn_conf.py /gunicorn_conf.py
COPY ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN groupadd -g 1337 textrig && \
    useradd -m -u 1337 -g textrig textrig

#COPY --chown=textrig:textrig ./textrig /app
USER textrig
#WORKDIR /app

EXPOSE 8000

ENTRYPOINT /entrypoint.sh $0 $@
CMD ["gunicorn", "textrig.main:app", "--config", "/gunicorn_conf.py"]