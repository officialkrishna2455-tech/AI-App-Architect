.PHONY: help dev dev-backend dev-frontend test build deploy clean install

help: ## Show this help message
	@echo "Requirement Compiler - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Installation ─────────────────────────────────────────────

install: ## Install all dependencies
	cd backend && pip install -r requirements.txt
	cd backend && python -m spacy download en_core_web_sm || true
	cd frontend && npm install

install-backend: ## Install backend dependencies only
	cd backend && pip install -r requirements.txt
	cd backend && python -m spacy download en_core_web_sm || true

install-frontend: ## Install frontend dependencies only
	cd frontend && npm install

# ── Development ──────────────────────────────────────────────

dev: ## Start both backend and frontend in development mode
	@echo "Starting backend on :8000 and frontend on :3000..."
	$(MAKE) -j2 dev-backend dev-frontend

dev-backend: ## Start backend development server
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend development server
	cd frontend && npm run dev

# ── Testing ──────────────────────────────────────────────────

test: ## Run all tests
	cd backend && python -m pytest tests/ -v --tb=short

test-coverage: ## Run tests with coverage report
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=html

test-pipeline: ## Run pipeline integration test
	cd backend && python -m pytest tests/test_pipeline.py -v

# ── Evaluation ───────────────────────────────────────────────

evaluate: ## Run the full evaluation framework (20 prompts)
	cd backend && python -m app.evaluation.runner

# ── Build ────────────────────────────────────────────────────

build: ## Build Docker images
	docker-compose build

build-frontend: ## Build frontend for production
	cd frontend && npm run build

# ── Deployment ───────────────────────────────────────────────

deploy: build ## Deploy using Docker Compose
	docker-compose up -d

deploy-stop: ## Stop deployed containers
	docker-compose down

deploy-logs: ## View deployment logs
	docker-compose logs -f

# ── Cleanup ──────────────────────────────────────────────────

clean: ## Clean build artifacts and caches
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/htmlcov 2>/dev/null || true
	rm -rf frontend/.next 2>/dev/null || true
	rm -rf frontend/node_modules 2>/dev/null || true

clean-db: ## Remove the SQLite database
	rm -f backend/requirement_compiler.db 2>/dev/null || true

# ── Database ─────────────────────────────────────────────────

db-init: ## Initialize the database
	cd backend && python -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"
