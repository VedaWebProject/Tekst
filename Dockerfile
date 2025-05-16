
# TEKST-WEB BUILDER IMAGE

FROM node:22.15.1-alpine3.20 AS web-builder
WORKDIR /tekst
COPY Tekst-Web/ ./Tekst-Web/
COPY Tekst-API/openapi.json ./Tekst-API/openapi.json
RUN cd Tekst-Web && npm install && npm run build-only -- --base=./


# PYTHON ALPINE BASE IMAGE

FROM python:3.13-alpine3.21 AS py-base
ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore


# TEKST-API BUILDER IMAGE

FROM py-base AS api-builder
WORKDIR "/tekst"

COPY --from=ghcr.io/astral-sh/uv:0.7.3 /uv /uvx /bin/
COPY Tekst-API/tekst/ ./tekst/
COPY Tekst-API/uv.lock* \
     Tekst-API/pyproject.toml \
     Tekst-API/README.md \
     Tekst-API/LICENSE \
     ./

RUN uv run pip install --upgrade \
    pip \
    setuptools \
    wheel

RUN uv export \
    --locked \
    --no-group dev \
    --no-hashes \
    --no-progress \
    --format requirements-txt \
    --output-file requirements.txt

RUN uv run pip wheel \
    --requirement requirements.txt \
    --wheel-dir deps

RUN uv build --wheel


# FINAL PRODUCTION IMAGE

FROM py-base AS prod
ENV FASTAPI_ENV=production
WORKDIR "/tekst"

RUN set -x && \
    addgroup -S tekst && \
    adduser -S tekst -G tekst

RUN apk update && \
    apk add --no-cache curl caddy

HEALTHCHECK \
    --interval=2m \
    --timeout=5s \
    --retries=3 \
    --start-period=30s \
    CMD curl http://localhost:8000/status || exit 1

COPY --from=api-builder /tekst/deps/ api/deps/
COPY --from=api-builder /tekst/dist/ api/dist/
COPY --from=web-builder /tekst/Tekst-Web/dist/ /var/www/html/

RUN chown -R tekst:tekst /var/www/html/

RUN python3 -m pip install \
    --no-index \
    --find-links api/deps/ \
    api/dist/*.whl && \
    rm -rf api

RUN python3 -m pip install \
    "uvicorn[standard]==0.32.0" \
    "gunicorn==23.0.0"

COPY docker/caddy/Caddyfile /etc/caddy/Caddyfile
COPY docker/gunicorn/gunicorn_conf.py /etc/gunicorn/
COPY docker/entrypoint.sh /usr/local/bin/

VOLUME /var/www/tekst/static/
EXPOSE 8080
USER tekst

LABEL org.opencontainers.image.description="A collaborative research platform for resources on natural language texts"

ENTRYPOINT ["entrypoint.sh"]
CMD ["gunicorn", "tekst.app:app", "--config", "/etc/gunicorn/gunicorn_conf.py"]
