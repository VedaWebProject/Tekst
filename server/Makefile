SHELL = /bin/sh
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
	@echo "This is TextRig-$(version) speaking. Help will arrive shortly."
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
	@. $(virtualenv)/bin/activate ; \
	isort . --quiet ; \
	black .
.PHONY: pretty


test: venv
	@. $(virtualenv)/bin/activate ; \
	flake8 . && \
	pytest \
		--cov=$(src) \
		--cov-config=.coveragerc \
		$(tests)/
.PHONY: test


run: venv
	@. $(virtualenv)/bin/activate ; \
	cd $(src) ; \
	$(python) -m textrig
.PHONY: run


clean:
	@setopt -s globstar ; \
	rm -rf \
		**/__pycache__ \
		.pytest_cache \
		.coverage \
		htmlcov \
.PHONY: clean
