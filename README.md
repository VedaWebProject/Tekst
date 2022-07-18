# TextRig Server

This is the code repository for the **server** part of the TextRig platform. For general information on TextRig, please visit the main [TextRig repository](https://github.com/VedaWebProject/TextRig).


## Development

1) This project is configured to use [Poetry](https://python-poetry.org) as its build tool. You can install Poetry from [here](https://python-poetry.org/docs/master/#installation).
2) Install project and dependencies (from project directory): `poetry install`
3) You can now use `poetry build`, `poetry run python textrig` [and so on](https://python-poetry.org/docs/basic-usage/).
4) The project has some very convenient tasks configured that can be run with [Poe the Poet](https://github.com/nat-n/poethepoet) (a task runner). This is optional, but helps a lot. You can install it form [here](https://github.com/nat-n/poethepoet). These are some of the configured tasks that can be run via `poe <task>`:

```
format         Run black to format code base
style          Check code style using black
isort          Run isort to sort imports
isort-check    Check import order using isort
lint           Run flake8 linter
test           Run test suite with pytest
run            Run the application
pretty         Format code and sort imports in one go
check          Run all checks on code base: tests, code style, import order
clean          Cleanup of generated files (won't work on Windows)
```