CABINET = cd cabinet && uv run

.PHONY: up down test lint format typecheck check

up:
	docker compose up -d

down:
	docker compose down

test:
	$(CABINET) pytest

lint:
	$(CABINET) ruff check .
	$(CABINET) ruff format --check .

format:
	$(CABINET) ruff check --fix .
	$(CABINET) ruff format .

typecheck:
	$(CABINET) mypy .

check: lint typecheck test
