
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
COVERAGE := $(VENV)/bin/coverage
GUNICORN := $(VENV)/bin/gunicorn


.PHONY: all install run gunicorn coverage clean deepclean
all: install coverage


install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install pytest coverage


run:
	$(PYTHON) main.py


gunicorn:
	$(GUNICORN) -c app/settings/gunicorn.py


coverage:
	$(COVERAGE) run --rcfile=app/settings/.coveragerc -m pytest -v
	$(COVERAGE) report
	$(COVERAGE) html


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


deepclean: clean
	@rm -rf $(VENV)
