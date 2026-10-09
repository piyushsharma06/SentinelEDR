.PHONY: help install backend-dev frontend-dev agent-dev test test-backend test-agent build seed docker-up docker-down lint

help:
	@echo "SentinelEDR Development Commands:"
	@echo "  make install        Install backend and agent Python dependencies, and frontend npm packages"
	@echo "  make backend-dev    Start FastAPI backend development server on localhost:8000"
	@echo "  make frontend-dev   Start React Vite frontend development server on localhost:5173"
	@echo "  make agent-dev      Run the Windows endpoint agent locally"
	@echo "  make seed           Seed deterministic synthetic demo data (benign & simulated attacks)"
	@echo "  make test           Run all backend, detection engine, and agent tests"
	@echo "  make test-backend   Run backend and detection unit/integration tests"
	@echo "  make test-agent     Run agent telemetry collector & queue unit tests"
	@echo "  make build          Build production bundle for frontend"
	@echo "  make docker-up      Start full containerized deployment (Postgres + Backend + Frontend)"
	@echo "  make docker-down    Stop containerized deployment"

install:
	pip install -r backend/requirements.txt
	pip install -r agent/requirements.txt
	cd frontend && npm install

backend-dev:
	python -m uvicorn app.main:app --app-dir backend --reload --port 8000 --host 127.0.0.1

frontend-dev:
	cd frontend && npm run dev

agent-dev:
	python -m sentinel_agent.main --config agent/config.yaml

seed:
	python -m backend.app.demo.seed

test:
	pytest backend/tests agent/tests -v

test-backend:
	pytest backend/tests -v

test-agent:
	pytest agent/tests -v

build:
	cd frontend && npm run build

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down
