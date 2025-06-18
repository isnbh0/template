APP_NAME := {{cookiecutter.project_slug}}
PATHS := $(APP_NAME) tests

init:
	./setup.sh
	git init
	pre-commit install
	uv sync
	git add .
	-pre-commit run --all-files
	git add .
	git commit -m "Initial commit"

test:
	uv run pytest tests -v --cov

f401:
	uv run ruff check --select F401 --fix $(PATHS)

isort:
	uv run ruff check --select I --fix $(PATHS)

black:
	uv run ruff format $(PATHS)

format: f401 isort black

lint:
	uv run ruff check $(PATHS)
