SHELL = /bin/sh
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
.DEFAULT_GOAL := hello


.PHONY: hello
hello:
	@echo "TextRig says HELLO!"

.PHONY: venv
venv: .venv/touchfile

.venv/touchfile: requirements.txt
	@test -d .venv || python3 -m venv .venv --prompt textrig-dev
	@. .venv/bin/activate; pip install -Ur requirements.txt
	@touch .venv/touchfile
	@printf "\n\n"

.PHONY: test
test: venv
	@. .venv/bin/activate ; \
		pytest tests/

.PHONY: run
run: venv
	@. .venv/bin/activate ; \
		python -m textrig

.PHONY: clean
clean:
	@rm -rf \
		.venv \
		.pytest_cache \
		__pycache__ **/__pycache__ \
