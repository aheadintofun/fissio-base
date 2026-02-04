.PHONY: help up down restart logs status clean reset jupyter superset duckdb frontend build

help:
	@echo "Fissio Base - Central Analytics & Embeddable Dashboards"
	@echo ""
	@echo "Commands:"
	@echo "  make up        Start all services"
	@echo "  make down      Stop all services"
	@echo "  make restart   Restart all services"
	@echo "  make logs      Follow service logs"
	@echo "  make status    Show service status"
	@echo "  make clean     Stop and remove volumes"
	@echo "  make reset     Full reset (removes all data)"
	@echo "  make build     Rebuild frontend image"
	@echo ""
	@echo "Individual services:"
	@echo "  make frontend  Start only Frontend"
	@echo "  make jupyter   Start only Jupyter"
	@echo "  make superset  Start only Superset"
	@echo "  make duckdb    Start only DuckDB UI"
	@echo ""
	@echo "Access:"
	@echo "  Frontend: http://localhost:8080 (unified dashboard)"
	@echo "  Jupyter:  http://localhost:8888 (token: fissio)"
	@echo "  Superset: http://localhost:8088 (admin/admin)"
	@echo "  DuckDB:   http://localhost:5522"

up:
	docker compose up -d --build
	@echo ""
	@echo "Fissio Base starting..."
	@echo ""
	@echo "Access:"
	@echo "  Frontend: http://localhost:8080 (unified dashboard)"
	@echo "  Jupyter:  http://localhost:8888 (token: fissio)"
	@echo "  Superset: http://localhost:8088 (admin/admin)"
	@echo "  DuckDB:   http://localhost:5522"
	@echo ""
	@echo "Run 'make logs' to follow startup progress"

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

status:
	docker compose ps

clean:
	docker compose down -v

reset:
	@echo "WARNING: This will delete all data including notebooks and DuckDB files!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	docker compose down -v
	rm -rf data/*.duckdb data/*.parquet
	docker compose up -d --build

build:
	docker compose build frontend

frontend:
	docker compose up -d frontend
	@echo "Frontend: http://localhost:8080"

jupyter:
	docker compose up -d jupyter
	@echo "Jupyter: http://localhost:8888 (token: fissio)"

superset:
	docker compose up -d superset-init superset
	@echo "Superset: http://localhost:8088 (admin/admin)"

duckdb:
	docker compose up -d duckdb-ui
	@echo "DuckDB UI: http://localhost:5522"
