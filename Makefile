.PHONY: help up down restart logs status clean reset jupyter superset

help:
	@echo "Fissio Base - Central Analytics & Embeddable Dashboards"
	@echo ""
	@echo "Commands:"
	@echo "  make up        Start all services (Jupyter + Superset)"
	@echo "  make down      Stop all services"
	@echo "  make restart   Restart all services"
	@echo "  make logs      Follow service logs"
	@echo "  make status    Show service status"
	@echo "  make clean     Stop and remove volumes"
	@echo "  make reset     Full reset (removes all data)"
	@echo ""
	@echo "Individual services:"
	@echo "  make jupyter   Start only Jupyter"
	@echo "  make superset  Start only Superset"
	@echo ""
	@echo "Access:"
	@echo "  Jupyter:  http://localhost:8888 (token: fissio)"
	@echo "  Superset: http://localhost:8088 (admin/admin)"
	@echo ""
	@echo "Embedding:"
	@echo "  Dashboard: http://localhost:8088/superset/dashboard/<id>/?standalone=true"
	@echo "  Chart:     http://localhost:8088/superset/explore/?standalone=true&slice_id=<id>"

up:
	docker compose up -d
	@echo ""
	@echo "Fissio Base starting..."
	@echo ""
	@echo "Access:"
	@echo "  Jupyter:  http://localhost:8888 (token: fissio)"
	@echo "  Superset: http://localhost:8088 (admin/admin)"
	@echo ""
	@echo "Embed dashboards in other Fissio apps:"
	@echo "  <iframe src=\"http://localhost:8088/superset/dashboard/1/?standalone=true\"></iframe>"
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
	docker compose up -d

jupyter:
	docker compose up -d jupyter
	@echo "Jupyter: http://localhost:8888 (token: fissio)"

superset:
	docker compose up -d superset-init superset
	@echo "Superset: http://localhost:8088 (admin/admin)"
