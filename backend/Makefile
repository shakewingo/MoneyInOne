# MoneyInOne Backend Makefile

.PHONY: help install dev test lint format clean docker-build docker-up docker-down migrate

# Default target
help:
	@echo "Available commands:"
	@echo "  install     Install dependencies"
	@echo "  dev         Start development server"
	@echo "  test        Run tests"
	@echo "  lint        Run linting"
	@echo "  format      Format code"
	@echo "  clean       Clean up generated files"
	@echo "  docker-build Build Docker image"
	@echo "  docker-up   Start Docker services"
	@echo "  docker-down Stop Docker services"

# Development setup
install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing
test:
	pytest -v --cov=app --cov-report=html --cov-report=term-missing

test-fast:
	pytest -v -x

# Code quality
lint:
	ruff check app/ tests/
	black --check app/ tests/

format:
	black app/ tests/
	ruff --fix app/ tests/

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

# Docker commands
docker-build:
	docker build -t moneyinone-backend .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Development helpers
shell:
	python -c "import asyncio; from app.core.database import database; from app.models import *; print('Database models imported')"

# Production commands
prod-up:
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.prod.yml down
