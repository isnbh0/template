# {{cookiecutter.project_name}}

{{cookiecutter.project_short_description}}

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management. To get started:

1. Install uv if you haven't already:
   ```
   pip install uv
   ```

2. Install the project dependencies:
   ```
   uv sync
   ```

## Development

- Run tests: `uv run pytest`
- Run linter: `uv run ruff check .`
