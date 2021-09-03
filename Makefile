SHELL = /bin/bash -eo pipefail

.PHONY: install-python-dependencies
install-python-dependencies:
	python -m pip install --disable-pip-version-check --requirement dev-requirements.txt

.PHONY: lint-editorconfig
lint-editorconfig:
	ec

.PHONY: lint-dockerfile
lint-dockerfile:
	find $(PWD) -name Dockerfile* -print0 | xargs -0 -I % hadolint %

.PHONY: lint-all
lint-all: | lint-editorconfig lint-dockerfile

.PHONY: clean-python
clean-python:
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

.PHONY: test-python
test-python:
	tox
