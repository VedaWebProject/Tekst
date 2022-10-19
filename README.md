# TextRig Server

[![tests](https://github.com/VedaWebProject/textrig-server/actions/workflows/tests.yml/badge.svg)](https://github.com/VedaWebProject/textrig-server/actions/workflows/tests.yml)
[![style checks](https://github.com/VedaWebProject/textrig-server/actions/workflows/style.yml/badge.svg)](https://github.com/VedaWebProject/textrig-server/actions/workflows/style.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This is the code repository for the **server** part of the TextRig platform. For general information on TextRig, please visit the main [TextRig repository](https://github.com/VedaWebProject/textrig).


## Development

1) This project is configured to use [Poetry](https://python-poetry.org) as its build tool. You can install Poetry from [here](https://python-poetry.org/docs/master/#installation).
2) Install project and dependencies (from project directory): `poetry install`
3) You can now use `poetry build`, `poetry run python textrig` [and so on](https://python-poetry.org/docs/basic-usage/).
4) The project has some very convenient tasks configured that can be run with [Poe the Poet](https://github.com/nat-n/poethepoet) (a task runner). This is optional, but helps a lot. You can install it form [here](https://github.com/nat-n/poethepoet), tasks can then be run via `poe <task>`. You'll get a commented overview of the configured tasks if you run `poe` without any arguments or [here](pyproject.toml).
