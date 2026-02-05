# Fissio Base

Central analytics and dashboard platform for the Fissio suite. Provides a unified frontend with Jupyter notebooks, Apache Superset dashboards, and DuckDB SQL editor - all with Fissio dark theme styling.

Part of the **Fissio Platform** for nuclear site development:
- **fissio-site** (port 8000) - Site selection & CAD designer
- **fissio-docs** (port 8001/3000) - Document intelligence & RAG
- **fissio-crmi** (port 3001) - CRM for nuclear operations
- **fissio-base** (port 8080) - Analytics & embeddable dashboards ← *this repo*

## Quick Start

```bash
# 1. Start services
make up

# 2. Open the unified dashboard
open http://localhost:8080
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           fissio-base :8080                              │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Frontend (Fissio Dark Theme)            │  │
│  │                         Unified Dashboard                          │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                    │                │                │                   │
│  ┌─────────────────┼────────────────┼────────────────┼───────────────┐  │
│  │                 ▼                ▼                ▼               │  │
│  │  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐         │  │
│  │  │    Jupyter    │  │   Superset    │  │   DuckDB UI   │         │  │
│  │  │     :8888     │  │     :8088     │  │     :5522     │         │  │
│  │  │  Notebooks    │  │  Dashboards   │  │  SQL Editor   │         │  │
│  │  └───────────────┘  └───────────────┘  └───────────────┘         │  │
│  │                                                                   │  │
│  │  ┌───────────────────────────────────────────────────────────┐   │  │
│  │  │                        ./data                              │   │  │
│  │  │           fissio.duckdb + Parquet files                   │   │  │
│  │  └───────────────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Services

| Service | Port | Purpose | Credentials |
|---------|------|---------|-------------|
| **Frontend** | 8080 | Unified dashboard with Fissio styling | - |
| **Jupyter** | 8888 | Interactive notebooks | token: `fissio` |
| **Superset** | 8088 | Dashboards & visualizations | admin/admin |
| **DuckDB UI** | 5522 | SQL editor (import Parquet via UI) | - |

## Features

- **Unified Dashboard** - Single entry point with navigation to all analytics tools
- **Fissio Dark Theme** - Consistent styling with other Fissio apps (#00d492 accent)
- **Tabler Icons** - Same icon library as fissio-crmi
- **Embeddable Dashboards** - Superset configured for iframe embedding
- **DuckDB SQL Editor** - [Duck-UI](https://github.com/ibero-data/duck-ui) for direct database access

## Commands

```bash
make up        # Start all services
make down      # Stop all services
make logs      # Follow service logs
make build     # Rebuild frontend image
make clean     # Stop and remove volumes
make reset     # Full reset (removes all data)

# Individual services
make frontend  # Start only Frontend
make jupyter   # Start only Jupyter
make superset  # Start only Superset
make duckdb    # Start only DuckDB UI
```

## Data Architecture

### DuckDB Schemas

| Schema | Purpose |
|--------|---------|
| `plants` | Power plant facilities, equipment, outages |
| `regulatory` | NRC inspections, violations, enforcement |
| `market` | Electricity prices, capacity markets |

### File Organization

```
data/
├── fissio.duckdb              # Main analytical database
├── plants_facilities.parquet   # Exported for dashboards
├── regulatory_inspections.parquet
└── market_prices.parquet
```

## Embedding Dashboards

Superset is configured to allow embedding dashboards and charts into other Fissio apps via iframe.

### Embed URLs

```
# Dashboard
http://localhost:8088/superset/dashboard/<id>/?standalone=true

# Single Chart
http://localhost:8088/superset/explore/?standalone=true&slice_id=<id>
```

### Example

```html
<iframe
  src="http://localhost:8088/superset/dashboard/1/?standalone=true"
  width="100%"
  height="600"
  frameborder="0">
</iframe>
```

### CORS Origins (Allowed)

- `http://localhost:8000` (fissio-site)
- `http://localhost:3000` (fissio-docs UI)
- `http://localhost:3001` (fissio-crmi)
- `https://fissio.com` (production)

## Workflow

1. **Seed the database** - Run `make seed` to populate DuckDB with power industry data
2. **Query in Jupyter** - Primary interface for querying the seeded DuckDB database
3. **Explore in DuckDB UI** - Import Parquet files via UI for ad-hoc SQL (WebAssembly-based)
4. **Build in Superset** - Create production dashboards and charts
5. **Embed everywhere** - Add dashboards to fissio-site, fissio-docs, fissio-crmi, or fissio.com

### DuckDB UI Note
Duck-UI runs DuckDB in-browser via WebAssembly. To query the seeded data:
- Import Parquet files from `/data/` (e.g., `global_power_plants.parquet`)
- Or use **Jupyter** which connects directly to `fissio.duckdb`

## Sample Notebooks

| Notebook | Description |
|----------|-------------|
| `00_getting_started.ipynb` | DuckDB setup, sample schema, basic queries |

## Running the Full Platform

```bash
# Terminal 1: Site selection app
cd ~/fissio-site && make serve

# Terminal 2: Document server
cd ~/fissio-docs && docker compose up

# Terminal 3: CRM
cd ~/fissio-crmi && make up

# Terminal 4: Analytics & Dashboards
cd ~/fissio-base && make up
```

### Port Summary

| App | Port | URL |
|-----|------|-----|
| fissio-site | 8000 | http://localhost:8000 |
| fissio-docs API | 8001 | http://localhost:8001 |
| fissio-docs UI | 3000 | http://localhost:3000 |
| fissio-crmi | 3001 | http://localhost:3001 |
| **fissio-base** | **8080** | **http://localhost:8080** |
| └─ Jupyter | 8888 | http://localhost:8888 |
| └─ Superset | 8088 | http://localhost:8088 |
| └─ DuckDB UI | 5522 | http://localhost:5522 |

## Tech Stack

- **Frontend**: FastAPI + Jinja2 (Fissio dark theme)
- **Database**: DuckDB (analytical SQL)
- **Notebooks**: Jupyter Lab (scipy-notebook)
- **Dashboards**: Apache Superset
- **SQL Editor**: Duck-UI
- **Icons**: Tabler Icons
- **Container**: Docker Compose

## License

MIT

## Sources

- [DuckDB UI](https://duckdb.org/2025/03/12/duckdb-ui) - Official DuckDB web interface
- [Duck-UI](https://github.com/ibero-data/duck-ui) - Web-based DuckDB interface used in this stack
