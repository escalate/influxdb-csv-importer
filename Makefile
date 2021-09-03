SHELL = /bin/bash -eo pipefail

.PHONY: venv
venv: clean
	python3 -m venv venv

.PHONY: requirements
requirements:
	pip install --upgrade --requirement requirements.txt

.PHONY: dev-requirements
dev-requirements: requirements
	pip install --upgrade --requirement dev-requirements.txt

.PHONY: lint-editorconfig
lint-editorconfig:
	ec

.PHONY: lint-dockerfile
lint-dockerfile:
	find $(PWD) -name Dockerfile* -print0 | xargs -0 -I % hadolint %

.PHONY: lint
lint: | lint-editorconfig lint-dockerfile

.PHONY: test
test:
	tox

.PHONY: clean
clean:
	rm -rf venv/
	py3clean .
