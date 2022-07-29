FROM python:3.10-alpine AS builder
RUN apk add curl \
    && curl -sSL https://install.python-poetry.org | python3 -
WORKDIR /app
COPY . .
RUN /root/.local/bin/poetry build

FROM python:3.10-alpine
WORKDIR /app
COPY --from=builder /app/dist /tmp/textrig-dist
RUN python -m pip install --find-links=/tmp/textrig-dist/ textrig
RUN python -m pip install "uvicorn>=0.18.0,<0.19.0"
EXPOSE 8000
ENTRYPOINT ["gunicorn", "textrig.main:app"]
CMD "-w 4 -k uvicorn.workers.UvicornWorker"