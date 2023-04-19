# Tekst API

[![tests](https://github.com/VedaWebProject/tekst-api/actions/workflows/tests.yml/badge.svg)](https://github.com/VedaWebProject/tekst-api/actions/workflows/tests.yml)
[![style checks](https://github.com/VedaWebProject/tekst-api/actions/workflows/style.yml/badge.svg)](https://github.com/VedaWebProject/tekst-api/actions/workflows/style.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This is the code repository for the **server** part of the Tekst platform.
For general information on Tekst, please visit the main [Tekst repository](https://github.com/VedaWebProject/tekst).

## Development

1. Clone this repository via `git clone https://github.com/VedaWebProject/tekst-api.git`
2. This project is configured to use [Poetry](https://python-poetry.org) as its dependency management and build tool. You can install Poetry from [here](https://python-poetry.org/docs/master/#installation).
3. Install the project and its dependencies (from the project directory): `poetry install`
4. You can now use
   - `poetry run python -m tekst run --reload` to run the dev server
   - `poetry build` to build the project
   - [...and so on](https://python-poetry.org/docs/basic-usage/)
5. The project has some *very* convenient tasks configured that can be run with [Task](https://taskfile.dev/) (a task runner). This is optional, but it helps *a lot*. You can install it form [here](https://taskfile.dev/installation/). Tasks can then be run via `task <taskname>`. You'll get a commented overview of the configured tasks if you run `task` without any arguments (or look [here](Taskfile.yml)).
