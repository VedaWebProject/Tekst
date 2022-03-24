SHELL = /bin/sh
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))


# preps
virtualenv=~/.virtualenvs/textrig
pip=$(virtualenv)/bin/pip
syspython=python3.8
python=$(virtualenv)/bin/python


help:
	@echo "Help will arrive shortly."
.PHONY: help


venv: $(virtualenv)/touchfile
.PHONY: venv


$(virtualenv)/touchfile: requirements.txt
	@test -d $(virtualenv) || $(syspython) -m venv $(virtualenv) --prompt textrig-dev
	@. $(virtualenv)/bin/activate; $(pip) install -U pip; $(pip) install -Ur requirements.txt
	@touch $(virtualenv)/touchfile
	@printf "\n\n"


test: venv
	@. $(virtualenv)/bin/activate ; \
		$(python) -m pytest \
			--cov=textrig \
			--cov-config=.coveragerc \
			tests/
.PHONY: test


run: venv
	@. $(virtualenv)/bin/activate ; \
		$(python) -m textrig
.PHONY: run


clean:
	@rm -rf \
		.pytest_cache \
		.coverage \
		htmlcov \
		__pycache__ \
		**/__pycache__
.PHONY: clean
