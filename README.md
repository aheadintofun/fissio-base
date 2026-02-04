# Fissio Data

Nuclear industry analytics platform with DuckDB, Jupyter, and Superset.

Part of the **Fissio Platform** for nuclear site development:
- **fissio-site** (port 8000) - Site selection & CAD designer
- **fissio-docs** (port 8001/3000) - Document intelligence & RAG
- **fissio-crmi** (port 3001) - CRM for nuclear operations
- **fissio-data** (port 8888/8088) - Analytics & dashboards ← *this repo*

## Quick Start

```bash
# 1. Start services
make up

# 2. Access the apps
open http://localhost:8888   # Jupyter (token: fissio)
open http://localhost:8088   # Superset (admin/admin)
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│              Docker Compose                      │
├─────────────────────────┬───────────────────────┤
│       jupyter           │       superset        │
│   (scipy-notebook)      │   (apache/superset)   │
│      port 8888          │      port 8088        │
├─────────────────────────┴───────────────────────┤
│                    ./data                        │
│         (DuckDB + Parquet + CSV files)          │
└─────────────────────────────────────────────────┘
```

## Data Architecture

```
data/
├── fissio.duckdb          # Main analytical database
├── plants_facilities.parquet
├── regulatory_inspections.parquet
└── market_prices.parquet
```

### DuckDB Schemas

| Schema | Purpose |
|--------|---------|
| `plants` | Power plant facilities, equipment, outages |
| `regulatory` | NRC inspections, violations, enforcement |
| `market` | Electricity prices, capacity markets |

## Workflow

1. **Explore in Jupyter** - Load data, run analysis, prototype visualizations
2. **Export to Parquet** - Save insights as parquet files
3. **Dashboard in Superset** - Build interactive dashboards from validated analyses

## Commands

```bash
make up        # Start Jupyter + Superset
make down      # Stop all services
make logs      # Follow service logs
make jupyter   # Start only Jupyter
make superset  # Start only Superset
make clean     # Stop and remove volumes
make reset     # Full reset (removes all data)
```

## Connecting Superset to DuckDB

1. Open Superset at http://localhost:8088
2. Go to Settings → Database Connections → + Database
3. Select "Other" and use SQLAlchemy URI:
   ```
   duckdb:////app/data/fissio.duckdb
   ```
4. Or query parquet files directly:
   ```sql
   SELECT * FROM read_parquet('/app/data/plants_facilities.parquet')
   ```

## Sample Notebooks

| Notebook | Description |
|----------|-------------|
| `00_getting_started.ipynb` | DuckDB setup, sample schema, basic queries |

## Nuclear Industry Data Sources

Potential data to integrate:

| Source | Data Type | URL |
|--------|-----------|-----|
| NRC | Plant status, inspections | https://www.nrc.gov/reading-rm/doc-collections/ |
| EIA | Generation, capacity | https://www.eia.gov/electricity/data.php |
| IAEA | Global reactor database | https://pris.iaea.org/PRIS/ |
| PJM/ERCOT | Market prices | Various ISO websites |

## Fissio Platform Integration

### Running the Full Platform

```bash
# Terminal 1: Site selection app
cd ~/fissio-site && make serve

# Terminal 2: Document server
cd ~/fissio-docs && docker compose up

# Terminal 3: CRM
cd ~/fissio-crmi && make up

# Terminal 4: Analytics
cd ~/fissio-data && make up
```

### Port Summary

| App | Port | URL |
|-----|------|-----|
| fissio-site | 8000 | http://localhost:8000 |
| fissio-docs API | 8001 | http://localhost:8001 |
| fissio-docs UI | 3000 | http://localhost:3000 |
| fissio-crmi | 3001 | http://localhost:3001 |
| fissio-data Jupyter | 8888 | http://localhost:8888 |
| fissio-data Superset | 8088 | http://localhost:8088 |

## Tech Stack

- **Database**: DuckDB (analytical SQL)
- **Notebooks**: Jupyter Lab (scipy-notebook)
- **Dashboards**: Apache Superset
- **File Format**: Parquet (columnar, compressed)
- **Container**: Docker Compose

## License

MIT
