install:
	pip install --upgrade pip && \
	pip install -r requirements.txt && \
	pip install -r requirements-helpers.txt

format:
	black src --config pyproject.toml

check:
	black src --check --config pyproject.toml

lint:
	python -m flake8 -v

typecheck:
	mypy src

inspect: check lint typecheck
