VERSION 0.6
FROM python:3.10-slim-bullseye
WORKDIR /textrig

ENV PYTHONFAULTHANDLER=1
ENV PYTHONHASHSEED=random
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore
ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1
ENV VENV_PATH=/textrig/.venv


main-deps:

    ENV POETRY_VERSION=1.2.2
    ENV POETRY_VIRTUALENVS_IN_PROJECT=true
    ENV POETRY_NO_INTERACTION=1
    ENV PATH="/root/.local/bin:$VENV_PATH/bin:$PATH"

    RUN python3 -m pip install pipx && pipx install poetry==$POETRY_VERSION

    COPY pyproject.toml poetry.lock* ./
    RUN poetry run pip install --upgrade pip
    RUN poetry install --no-root --only main --sync


dev-deps:

    FROM +main-deps
    RUN poetry install --no-root --sync


build:

    FROM +main-deps

    RUN poetry run pip install --upgrade setuptools wheel

    COPY --dir textrig ./
    COPY README.md LICENSE MANIFEST.in ./

    RUN poetry build

    SAVE ARTIFACT ./dist/* dist/
    SAVE ARTIFACT ./dist/* AS LOCAL dist/


prod-env:

    FROM +main-deps
    COPY +build/dist/*.whl ./dist/

    RUN poetry run pip install \
            "uvicorn[standard]>=0.18,<1.0" \
            "gunicorn>=20.1,<21.0" && \
        poetry run pip install dist/*.whl

    SAVE ARTIFACT "$VENV_PATH"/* .venv/


prod:

    RUN apt-get update && apt-get install --no-install-recommends -y curl

    RUN groupadd -g 1337 textrig && \
        useradd -m -u 1337 -g textrig textrig
    USER textrig

    HEALTHCHECK --interval=2m --timeout=5s --retries=3 --start-period=30s \
        CMD curl -f http://localhost:8000 || exit 1

    COPY --dir +prod-env/.venv/ ./

    ARG TEXTRIG_VERSION=$(' \
        . .venv/bin/activate && \
        python3 -c "from textrig import __version__ as v; print(v)" \
    ')

    COPY ./gunicorn_conf.py ./docker-entrypoint.sh ./
    RUN chmod +x docker-entrypoint.sh

    EXPOSE 8000

    ENTRYPOINT ["/textrig/docker-entrypoint.sh"]
    CMD ["textrig.app:app", "--config", "gunicorn_conf.py"]

    SAVE IMAGE "textrig-server:$TEXTRIG_VERSION"
    SAVE IMAGE "textrig-server:latest"
