
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
COVERAGE := $(VENV)/bin/coverage
GUNICORN := $(VENV)/bin/gunicorn
GUNICORN_PID := /tmp/gunicorn
NGINX := /usr/local/nginx


.PHONY: all install run gunicorn coverage clean deepclean
all: install coverage


install: python

python:
	sudo apt-get install python3-venv
	sudo apt install python3-pip
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install pytest coverage


run:
	$(PYTHON) main.py


gunicorn:
	$(GUNICORN) -c app/settings/gunicorn.py --pid $(GUNICORN_PID)

stop_gunicorn:
	kill $$(cat GUNICORN_PID)


coverage:
	$(COVERAGE) run --rcfile=app/settings/.coveragerc -m pytest -v
	$(COVERAGE) report


clean:
	@rm -rf __pycache__
	@rm -rf */__pycache__
	@rm -rf */*/__pycache__
	@rm -rf */*/*/__pycache__
	@rm -rf .pytest_cache
	@rm -rf .coverage
	@rm -rf htmlcov
	@rm -f *.pyc
	@rm -f */*.pyc
	@rm -f */*/*.pyc
	@rm -f */*/*/*.pyc
	@rm -f *.log
	@rm -f api-error.log
	@rm -rf nginx*


deepclean: clean
	@rm -rf $(VENV)
