.PHONY: setup install test lint format clean build run deploy help

# Default target
.DEFAULT_GOAL := help

# Environment variables
PYTHON := python3
NODE := node
NPM := npm
VENV := env
VENV_BIN := $(VENV)/bin

# Colors for help messages
YELLOW := \033[33m
RESET := \033[0m

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2}'

setup: ## Set up development environment
	@echo "Setting up development environment..."
	$(PYTHON) -m venv $(VENV)
	. $(VENV_BIN)/activate && pip install --upgrade pip
	. $(VENV_BIN)/activate && pip install -r requirements.txt
	$(NPM) install
	$(NPM) run prepare
	@echo "Development environment setup complete"

install: ## Install dependencies
	. $(VENV_BIN)/activate && pip install -r requirements.txt
	$(NPM) install

test: ## Run tests
	. $(VENV_BIN)/activate && pytest
	$(NPM) test

test-coverage: ## Run tests with coverage
	. $(VENV_BIN)/activate && pytest --cov=env
	$(NPM) run test:coverage

lint: ## Run linters
	. $(VENV_BIN)/activate && flake8 env
	. $(VENV_BIN)/activate && mypy env
	. $(VENV_BIN)/activate && bandit -r env
	$(NPM) run lint

format: ## Format code
	. $(VENV_BIN)/activate && black env
	. $(VENV_BIN)/activate && isort env
	$(NPM) run format

clean: ## Clean build artifacts
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf coverage
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .tox
	rm -rf node_modules
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean ## Build the project
	$(NPM) run build
	. $(VENV_BIN)/activate && python setup.py build

run: ## Run the trading bot
	. $(VENV_BIN)/activate && $(PYTHON) env/main.py

run-dev: ## Run the trading bot in development mode
	$(NPM) run dev

deploy: ## Deploy the trading bot
	@echo "Deploying trading bot..."
	$(MAKE) clean
	$(MAKE) build
	@echo "Deployment complete"

update-deps: ## Update dependencies
	. $(VENV_BIN)/activate && pip-compile --upgrade requirements.in
	$(NPM) update

security-check: ## Run security checks
	. $(VENV_BIN)/activate && safety check
	. $(VENV_BIN)/activate && bandit -r env
	$(NPM) audit

docker-build: ## Build Docker image
	docker build -t quantum-solana-bot .

docker-run: ## Run Docker container
	docker run -d --name quantum-solana-bot quantum-solana-bot

docker-stop: ## Stop Docker container
	docker stop quantum-solana-bot
	docker rm quantum-solana-bot

logs: ## View logs
	tail -f logs/trading_bot.log

monitor: ## Monitor the trading bot
	$(NPM) run monitor

backup: ## Backup data
	@echo "Backing up data..."
	tar -czf backup-$(shell date +%Y%m%d-%H%M%S).tar.gz data/

restore: ## Restore data from backup
	@echo "Please provide backup file path:"
	@read -p "Backup file: " backup_file; \
	tar -xzf $$backup_file -C data/

init-dev: ## Initialize development environment
	pre-commit install
	husky install
	. $(VENV_BIN)/activate && pip install -r requirements-dev.txt

validate: ## Validate the project
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) security-check
	$(NPM) run typecheck

# Solana-specific commands
solana-keygen: ## Generate Solana keypair
	solana-keygen new -o env/.keypair

solana-balance: ## Check Solana balance
	solana balance

solana-airdrop: ## Request Solana airdrop (devnet)
	solana airdrop 1

# Database commands
db-migrate: ## Run database migrations
	. $(VENV_BIN)/activate && alembic upgrade head

db-rollback: ## Rollback database migration
	. $(VENV_BIN)/activate && alembic downgrade -1

# Cache commands
cache-clear: ## Clear cache
	redis-cli FLUSHALL

# Documentation commands
docs: ## Generate documentation
	. $(VENV_BIN)/activate && sphinx-build -b html docs/source docs/build
