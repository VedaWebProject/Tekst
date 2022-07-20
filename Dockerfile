FROM python:3.10-alpine AS build

RUN apk add curl
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app
COPY . .

RUN poetry build
RUN python -m pip install --no-index --find-links=dist/ textrig

RUN python -m textrig

EXPOSE 8000