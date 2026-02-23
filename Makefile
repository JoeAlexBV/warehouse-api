.PHONY: help install dev test coverage clean docker-build docker-up docker-down migrate

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make dev          - Run development server"
	@echo "  make test         - Run tests"
	@echo "  make coverage     - Run tests with coverage report"
	@echo "  make clean        - Remove cache files"
	@echo "  make docker-build - Build Docker images"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make migrate      - Run database migrations"
	@echo "  make format       - Format code with black"
	@echo "  make lint         - Lint code with flake8"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

coverage:
	pytest tests/ --cov=app --cov-report=html --cov-report=term

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api

migrate:
	alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " message; \
	alembic revision --autogenerate -m "$$message"

format:
	black app/ tests/

lint:
	flake8 app/ tests/