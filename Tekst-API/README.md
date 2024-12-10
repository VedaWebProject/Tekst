# Tekst API

![GitHub Workflow Status (tests)](https://img.shields.io/github/actions/workflow/status/VedaWebProject/Tekst/server-tests.yml?label=server%20tests)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

This project holds the codebase for the **server** part of the Tekst platform.
For general information on Tekst, visit the [Tekst repository](https://github.com/VedaWebProject/tekst).

## Development

1. Clone this repository via `git clone https://github.com/VedaWebProject/Tekst-API.git`
2. This project is configured to use [uv](https://docs.astral.sh/uv/) as its project management tool. You can install **uv**** from [here](https://docs.astral.sh/uv/getting-started/installation/).
3. Install the project and its dependencies (from the project directory): `uv sync`
4. You can now use
   - `uv run fastapi dev tekst/app.py` to run the dev server
   - [...and so on](https://docs.astral.sh/uv/reference/cli/)
5. The project has some *very* convenient tasks configured that can be run with [Task](https://taskfile.dev/) (a task runner). This is optional, but it helps *a lot*. You can install it form [here](https://taskfile.dev/installation/). Tasks can then be run via `task <taskname>`. You'll get a commented overview of the configured tasks if you run `task` without any arguments (or look [here](Taskfile.yml)).
