# Tekst API

![GitHub Workflow Status (tests)](https://img.shields.io/github/actions/workflow/status/VedaWebProject/Tekst/server-tests.yml?label=server%20tests)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

This project holds the codebase for the **server** part of the Tekst platform.
For general information on Tekst, visit the [Tekst repository](https://github.com/VedaWebProject/tekst).

## Development

1. Clone this repository via `git clone https://github.com/VedaWebProject/Tekst-API.git`
2. This project is configured to use [Poetry](https://python-poetry.org) as its dependency management and build tool. You can install Poetry from [here](https://python-poetry.org/docs/master/#installation).
3. Install the project and its dependencies (from the project directory): `poetry install`
4. You can now use
   - `poetry run python -m tekst run --reload` to run the dev server
   - `poetry build` to build the project
   - [...and so on](https://python-poetry.org/docs/basic-usage/)
5. The project has some *very* convenient tasks configured that can be run with [Task](https://taskfile.dev/) (a task runner). This is optional, but it helps *a lot*. You can install it form [here](https://taskfile.dev/installation/). Tasks can then be run via `task <taskname>`. You'll get a commented overview of the configured tasks if you run `task` without any arguments (or look [here](Taskfile.yml)).
