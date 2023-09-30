set windows-shell := ["C:\\Program Files\\Git\\bin\\sh.exe", "-c"]

_default: tasks

# List tasks
tasks:
	@just --list --unsorted

_setup_poetry:
	poetry install

# Setup project
setup: _setup_poetry
	poetry run pre-commit install

# Organize imports
sort:
	poetry run isort --profile black --line-length 88 .

# Format code
format:
	poetry run black .

# Organize imports & Format code
lint:
	poetry check
	@just sort
	@just format