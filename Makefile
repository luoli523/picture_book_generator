VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(PYTHON) -m pip

.PHONY: help venv setup install editable check-venv api-dev gradio-dev test lint format

help:
	@echo "Available targets:"
	@echo "  make setup      - Create .venv, install dependencies and project package"
	@echo "  make api-dev    - Run FastAPI server on :8000 using .venv"
	@echo "  make gradio-dev - Run Gradio app on :7860 using .venv"
	@echo "  make test       - Run tests using .venv"
	@echo "  make lint       - Run ruff check using .venv"
	@echo "  make format     - Run ruff format using .venv"

venv:
	python3 -m venv $(VENV)

setup: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

install: check-venv
	$(PIP) install -r requirements.txt

editable: check-venv
	$(PIP) install -e .

check-venv:
	@test -x "$(PYTHON)" || (echo "Missing .venv. Run: make setup"; exit 1)

api-dev: check-venv
	PYTHONPATH=src $(PYTHON) -m uvicorn apps.api.app.main:app --reload --port 8000

gradio-dev: check-venv
	$(PYTHON) app.py

test: check-venv
	PYTHONPATH=src $(PYTHON) -m pytest -v

lint: check-venv
	$(PYTHON) -m ruff check src tests apps

format: check-venv
	$(PYTHON) -m ruff format src tests apps

