SHELL = /bin/bash
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))


# preps
virtualenv=$(ROOT_DIR)/.venv
pip=$(virtualenv)/bin/pip
syspython=python3
python=$(virtualenv)/bin/python
src=$(ROOT_DIR)/src
tests=$(ROOT_DIR)/tests
version=$(shell $(python) setup.py --version)


help:
	@echo "This is TextRig server v$(version) speaking. Help will arrive shortly."
.PHONY: help


venv: $(virtualenv)/touchfile
.PHONY: venv


$(virtualenv)/touchfile: requirements.txt
	@test -d $(virtualenv) || $(syspython) -m venv $(virtualenv) --prompt textrig-dev
	@. $(virtualenv)/bin/activate ; \
	$(pip) install -U pip ; \
	$(pip) install -Ur requirements.txt
	@touch $(virtualenv)/touchfile
	@printf "\n\n"


pretty: venv
	@printf "\n"
	$(virtualenv)/bin/isort .
	@printf "\n"
	$(virtualenv)/bin/black .
	@printf "\n"
.PHONY: pretty


test: venv
	@printf "\n"
	$(virtualenv)/bin/isort --check .
	@printf "\n"
	$(virtualenv)/bin/black --check .
	@printf "\n"
	$(virtualenv)/bin/pflake8 .
	@printf "\n"
	$(virtualenv)/bin/pytest
	@printf "\n"
.PHONY: test


run: venv
	@. $(virtualenv)/bin/activate ; \
	cd $(src) ; \
	$(python) -m textrig
.PHONY: run


clean:
	@shopt -s globstar ; \
	rm -rf \
		**/__pycache__ \
		.pytest_cache \
		.coverage \
		htmlcov
.PHONY: clean
