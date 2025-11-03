# Tekst API

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://docs.astral.sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff)

This project holds the codebase for the **server** part of the Tekst platform.
For general information on Tekst, visit the [Tekst repository](https://github.com/VedaWebProject/tekst).

## Development

1. Clone the parent repository via `git clone https://github.com/VedaWebProject/Tekst.git`
2. This project (in `Tekst-API/`) is configured to use [uv](https://docs.astral.sh/uv/) as its project management tool. You can install **uv**** from [here](https://docs.astral.sh/uv/getting-started/installation/).
3. Install the project and its dependencies (from the `Tekst-API/` project directory): `uv sync`
4. Run the development environment
   - `uv run fastapi dev tekst/app.py` to run the dev server ([...and so on](https://docs.astral.sh/uv/reference/cli/))
   - Local development also needs all the services running (MongoDB, Elasticsearch + some optional extras). The easiest way is to use the development compose stack in `../dev/compose.yml`. This also contains a Caddy (web server) that manages routing of requests to the client dev server and the API. See [this](.justfile) for reference.
5. The project has some _very_ convenient recipes configured that can be run with [just](https://just.systems/man/en/packages.html) (a task runner). This is optional, but it helps _a lot_. Recipes can then be run via `just <recipe name>`. You'll get a commented overview of the configured recipes if you run `just` without any arguments (or look [here](.justfile)).
