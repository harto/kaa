.PHONY: all check lint test

all: venv

check: lint test

lint: | venv
	venv/bin/pylint kaa test/*.py

test: | venv
	source venv/bin/activate && bin/test

venv: requirements-dev.txt
	python -m venv venv
	venv/bin/pip install -U pip
	venv/bin/pip install -r requirements-dev.txt
	touch venv
