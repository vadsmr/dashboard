CABINET = cd cabinet && uv run
COLLECTOR = cd collector && uv run

.PHONY: up down migrate logs test lint format typecheck check

up:
	docker compose up -d --build

down:
	docker compose down

migrate:
	docker compose exec cabinet python manage.py migrate
	docker compose run --rm collector-migrate

logs:
	docker compose logs -f

test:
	$(CABINET) pytest

	$(COLLECTOR) pytest

lint:
	$(CABINET) ruff check .
	$(CABINET) ruff format --check .

	$(COLLECTOR) ruff check .
	$(COLLECTOR) ruff format --check .

format:
	$(CABINET) ruff check --fix --exit-zero .
	$(CABINET) ruff format .

	$(COLLECTOR) ruff check --fix --exit-zero .
	$(COLLECTOR) ruff format .

typecheck:
	$(CABINET) mypy .

	$(COLLECTOR) mypy .

check: lint typecheck test
