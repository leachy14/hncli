setup:
	python -m venv .venv && .venv/bin/pip install -e .

format:
	ruff check . 