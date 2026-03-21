.PHONY: dev stop build test lint clean

# Development
dev:
	docker compose up --build

dev-d:
	docker compose up --build -d

stop:
	docker compose down

# Build
build:
	docker compose build --no-cache

# Backend
backend-shell:
	docker compose exec backend bash

backend-test:
	docker compose exec backend pytest -v

backend-lint:
	docker compose exec backend ruff check app/

# Frontend
frontend-shell:
	docker compose exec frontend sh

# Logs
logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

logs-frontend:
	docker compose logs -f frontend

# Clean
clean:
	docker compose down -v --rmi local
	rm -rf frontend/node_modules
	find . -type d -name __pycache__ -exec rm -rf {} +
