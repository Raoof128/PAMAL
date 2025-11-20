.PHONY: install test lint format clean run help

PYTHON := python3
VENV := venv
BIN := $(VENV)/bin

help:
	@echo "Available commands:"
	@echo "  install    - Install dependencies in a virtual environment"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linters (ruff, mypy)"
	@echo "  format     - Format code (ruff)"
	@echo "  clean      - Remove artifacts"
	@echo "  run        - Run the API server"

install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -e .[dev]

test:
	$(BIN)/pytest --cov=. --cov-report=term-missing

lint:
	$(BIN)/ruff check .
	$(BIN)/mypy .

format:
	$(BIN)/ruff format .

clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -f pam_vault.db test_vault.db audit.log policies.yaml

run:
	$(BIN)/uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
