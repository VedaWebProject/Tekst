SHELL = /bin/sh
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))


help:
	@echo "Help will arrive shortly."
.PHONY: help


venv: .venv/touchfile
.PHONY: venv


.venv/touchfile: requirements.txt
	@test -d .venv || python3 -m venv .venv --prompt textrig-dev
	@. .venv/bin/activate; pip install -Ur requirements.txt
	@touch .venv/touchfile
	@printf "\n\n"


test: venv
	@. .venv/bin/activate ; \
		python -m pytest \
			--cov=textrig \
			--cov-config=.coveragerc \
			tests/
.PHONY: test


run: venv
	@. .venv/bin/activate ; \
		python -m textrig
.PHONY: run


clean:
	@rm -rf \
		.venv \
		.pytest_cache .coverage htmlcov \
		__pycache__ **/__pycache__
.PHONY: clean
