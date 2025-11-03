alias test := tests

# print list of available recipes
list:
  @just --list

# print API version
version:
  @echo "Test-API version: $(uv run python3 -c "from tekst import __version__ as v; print(v, end='')")"

# install dependencies
install:
  uv sync

# format code base, fix linting errors
fix:
  uv run ruff format .
  uv run ruff check . --fix

# check code formatting and style
check:
  uv run ruff format . --check
  uv run ruff check . --extend-select N

# run tests
tests ARGS="": install (services-up "test") && (services-down "test")
  -TEKST_CUSTOM_ENV_FILE=.env.test uv run pytest {{ARGS}}

# run dev environment
dev: (services-up "dev") && (services-down "dev")
  -TEKST_DEV_MODE=true uv run python3 -m tekst bootstrap
  @printf "\n\
    ╭───────────────────────────────────────────────────────╮\n\
    │ 🌐 Tekst-Web Dev Server ... http://127.0.0.1          │\n\
    │ 🐍 Tekst-API .............. http://127.0.0.1/api      │\n\
    │ 📖 API Docs ............... http://127.0.0.1/api/docs │\n\
    │ 📬 MailPit ................ http://127.0.0.1:8025     │\n\
    │ 📂 MongoExpress ........... http://127.0.0.1:8081     │\n\
    ╰───────────────────────────────────────────────────────╯\n\
    \n\
    "
  -TEKST_DEV_MODE=true uv run fastapi dev tekst/app.py

# export OpenAPI schema to openapi.json
schema:
  TEKST_DEV_MODE=true TEKST_LOG_LEVEL=warning uv run python3 -m tekst schema -f

# run full pre-commit toolchain
all:
  just fix
  just tests
  just check
  just schema

# build updated container images in services stack
services-build:
  docker compose -f ../dev/compose.yml --profile dev --profile test build

# run services stack
services-up SCOPE="test": gen-smtp-ssl-cert && wait-for-mongodb wait-for-elasticsearch
  docker compose -f ../dev/compose.yml --profile {{SCOPE}} -p tekst-{{SCOPE}} up --detach

# kill services stack
services-down SCOPE="test":
  docker compose -f ../dev/compose.yml --profile {{SCOPE}} -p tekst-{{SCOPE}} down --volumes

# clean up generated files
cleanup:
  uv run ruff clean
  rm -rf \
    */**/__pycache__ \
    */**/.pytest_cache \
    .ruff_cache \
    .coverage \
    dist \
    htmlcov \

[private]
wait-for-mongodb:
  @printf "Waiting for MongoDB service"; sleep 2; printf "\n"

[private]
wait-for-elasticsearch:
  @printf "Waiting for Elasticsearch service"; while ! $(curl -f 127.0.0.1:9200 > /dev/null 2>&1); do sleep 1; printf "."; done; printf "\n"

[private]
gen-smtp-ssl-cert:
  @cd ../dev/smtp-ssl && ./generate.sh
