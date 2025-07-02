.PHONY: help install format lint type-check test clean docker-build docker-run

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$1}'

install: ## Install dependencies
	pip install -r requirements.txt
	pre-commit install

format: ## Format code with black and isort
	black .
	isort .

lint: ## Run flake8 linting
	flake8 .

type-check: ## Run mypy type checking
	mypy app/

check: format lint type-check ## Run all code quality checks

test: ## Run tests (requires main database to be running)
	pytest

test-with-db: ## Run tests with database setup (starts main DB if needed)
	@if ! docker-compose ps | grep -q "db.*Up"; then \
		echo "Starting main database..."; \
		docker-compose up -d db; \
		echo "Waiting for database to be ready..."; \
		until docker-compose exec -T db pg_isready -U postgres; do sleep 1; done; \
	fi
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=app --cov-report=html --cov-report=term

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -f .coverage

docker-build: ## Build Docker image
	docker-compose build

docker-run: ## Run application with Docker Compose
	docker-compose up -d

docker-stop: ## Stop Docker containers
	docker-compose down

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-migrate: ## Run database migrations in Docker
	docker-compose exec app alembic upgrade head

docker-migrate-create: ## Create new migration in Docker (usage: make docker-migrate-create name=migration_name)
	docker-compose exec app alembic revision --autogenerate -m "$(name)"

dev: ## Run development server
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate: ## Run database migrations
	alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create name=migration_name)
	alembic revision --autogenerate -m "$(name)"
