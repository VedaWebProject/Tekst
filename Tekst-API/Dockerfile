
# =====================
# BASE IMAGE
# =====================

FROM python:3.10-slim-bullseye AS base

COPY --chmod=0644 <<"EOF" /etc/apt/apt.conf
APT::Get::Assume-Yes "true";
APT::Install-Recommends "0";
APT::Install-Suggests "0";
APT::Sandbox::User "root";
EOF

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore \
    WORKDIR_PATH="/tekst"


# =====================
# BUILDER
# =====================

FROM base AS builder

ENV POETRY_VERSION=1.2.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PATH="/root/.local/bin:$PATH"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN python3 -m pip install pipx && \
    pipx install poetry==$POETRY_VERSION

WORKDIR "$WORKDIR_PATH"
COPY ./poetry.lock* ./pyproject.toml ./

RUN poetry run pip install --upgrade \
        pip \
        setuptools \
        wheel

# export dependencies as requirements.txt
RUN poetry export \
        --without-hashes \
        --without-urls \
        --format requirements.txt \
        --output requirements.txt

# build wheels for dependencies
RUN poetry run pip wheel \
        --requirement requirements.txt \
        --wheel-dir deps

# copy app source and build wheel
COPY tekst/ tekst/
COPY README.md LICENSE ./
RUN poetry build --format wheel


# ==============
# PROD APP IMAGE
# ==============

FROM base AS prod

ENV FASTAPI_ENV=production

# install needed OS packages
RUN apt-get update && \
    apt-get install curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR "$WORKDIR_PATH"

# copy app and dependencies
COPY --from=builder "$WORKDIR_PATH"/deps/ deps/
COPY --from=builder "$WORKDIR_PATH"/dist/ dist/

# install app and dependencies
RUN python3 -m pip install \
        --no-index \
        --find-links deps \
        dist/*.whl

# cleanup
RUN rm -rf dist deps

# install uvicorn ASGI workers and gunicorn WSGI server
RUN python3 -m pip install \
        "uvicorn[standard]==0.30.0" \
        "gunicorn==22.0.0"

HEALTHCHECK \
    --interval=2m \
    --timeout=5s \
    --retries=3 \
    --start-period=30s \
    CMD curl http://localhost:8000/status || exit 1

RUN groupadd -g 1000 tekst && \
    useradd -m -u 1000 -g tekst tekst

COPY ./deployment/gunicorn/gunicorn_conf.py ./
COPY ./deployment/entrypoint.sh /

USER tekst

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
