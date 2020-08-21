.PHONY: all check clean lint test

all: venv/bin/kaa

venv/bin/kaa: setup.py | venv
	venv/bin/python setup.py develop

venv: requirements-dev.txt
	python -m venv venv
	venv/bin/pip install -q -U pip
	venv/bin/pip install -q -r requirements-dev.txt
	touch venv

check: lint test

lint: | venv
	venv/bin/pylint src test

test: | venv venv/bin/kaa
	source venv/bin/activate && bin/test

clean:
	rm -rf venv
	git clean -dfX src test
