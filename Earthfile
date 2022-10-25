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


build-base:

    ENV POETRY_VERSION=1.2.2
    ENV POETRY_VIRTUALENVS_IN_PROJECT=true
    ENV POETRY_NO_INTERACTION=1
    ENV PATH="/root/.local/bin:$VENV_PATH/bin:$PATH"

    RUN python3 -m pip install pipx && pipx install poetry==$POETRY_VERSION

    COPY pyproject.toml poetry.lock* ./
    RUN poetry run pip install --upgrade pip wheel setuptools


deps:

    FROM +build-base
    ARG DEV_DEPS=

    RUN poetry export \
        ${DEV_DEPS:+--with dev} \
        --without-hashes \
        --without-urls \
        --format requirements.txt \
        --output requirements.txt
    RUN poetry run pip wheel -r requirements.txt --wheel-dir=wheels

    SAVE ARTIFACT wheels /wheels
    SAVE ARTIFACT requirements.txt


build:

    FROM +build-base

    COPY --dir textrig ./
    COPY README.md LICENSE MANIFEST.in ./

    RUN poetry build

    SAVE ARTIFACT ./dist
    SAVE ARTIFACT ./dist/* AS LOCAL dist/


prod:

    # install gunicorn and uvicorn workers
    RUN python3 -m pip install \
        "uvicorn[standard]>=0.18,<1.0" \
        "gunicorn>=20.1,<21.0"

    # instal curl (for health check)
    RUN apt-get update && apt-get install --no-install-recommends -y curl

    # copy and install dependencies
    COPY --dir +deps/wheels ./
    COPY +deps/requirements.txt ./
    RUN python3 -m pip install --no-index --find-links=wheels -r requirements.txt

    # copy and install app
    COPY --dir +build/dist ./
    RUN python3 -m pip install dist/*.whl

    # cleanup
    RUN rm -rf dist wheels requirements.txt

    COPY ./gunicorn_conf.py ./

    HEALTHCHECK --interval=2m --timeout=5s --retries=3 --start-period=30s \
        CMD curl -f http://localhost:8000 || exit 1

    RUN groupadd -g 1337 textrig && \
        useradd -m -u 1337 -g textrig textrig
    USER textrig

    EXPOSE 8000

    ENTRYPOINT ["gunicorn", "textrig.app:app", "--config", "gunicorn_conf.py"]

    # save Docker image
    ARG TEXTRIG_VERSION=$('python3 -c "from textrig import __version__ as v; print(v)"')
    SAVE IMAGE "textrig-server:$TEXTRIG_VERSION"
    SAVE IMAGE "textrig-server:latest"
