# Fissio Base

Central analytics and dashboard platform for the Fissio suite. Provides embeddable dashboards and data analysis capabilities across all Fissio apps.

Part of the **Fissio Platform** for nuclear site development:
- **fissio-site** (port 8000) - Site selection & CAD designer
- **fissio-docs** (port 8001/3000) - Document intelligence & RAG
- **fissio-crmi** (port 3001) - CRM for nuclear operations
- **fissio-base** (port 8888/8088) - Analytics & embeddable dashboards ← *this repo*

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
┌─────────────────────────────────────────────────────────────────────┐
│                         Fissio Platform                              │
├─────────────┬─────────────┬─────────────┬──────────────────────────┤
│ fissio-site │ fissio-docs │ fissio-crmi │      fissio.com          │
│   :8000     │  :8001/3000 │    :3001    │     (production)         │
├─────────────┴─────────────┴─────────────┴──────────────────────────┤
│                    ↑ Embedded Dashboards ↑                          │
├─────────────────────────────────────────────────────────────────────┤
│                        fissio-base                                   │
│  ┌─────────────────────────┬───────────────────────────────────┐   │
│  │       jupyter           │           superset                 │   │
│  │   (scipy-notebook)      │     (apache/superset)             │   │
│  │      port 8888          │        port 8088                  │   │
│  │                         │   • Embeddable charts             │   │
│  │   Data exploration      │   • Public dashboards             │   │
│  │   Analysis prototyping  │   • CORS enabled                  │   │
│  ├─────────────────────────┴───────────────────────────────────┤   │
│  │                        ./data                                │   │
│  │              (DuckDB + Parquet + CSV files)                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Embedding Dashboards

Superset is configured to allow embedding dashboards and charts into other Fissio apps via iframe.

### Step 1: Create a Dashboard in Superset

1. Open Superset at http://localhost:8088
2. Create charts and dashboards from your data
3. Go to Dashboard → Edit → Settings → Enable "Publish"

### Step 2: Get the Embed URL

For a dashboard:
```
http://localhost:8088/superset/dashboard/<dashboard_id>/?standalone=true
```

For a single chart:
```
http://localhost:8088/superset/explore/?standalone=true&slice_id=<chart_id>
```

### Step 3: Embed in Fissio Apps

**In fissio-site (Jinja2 template):**
```html
<iframe
  src="http://localhost:8088/superset/dashboard/1/?standalone=true"
  width="100%"
  height="600"
  frameborder="0">
</iframe>
```

**In fissio-docs (Next.js):**
```jsx
<iframe
  src="http://localhost:8088/superset/dashboard/1/?standalone=true"
  className="w-full h-[600px] border-0"
/>
```

**In fissio-crmi (Twenty CRM):**
Custom objects can link to dashboard URLs, or use webhooks to trigger data updates.

### CORS Configuration

The following origins are allowed for embedding:
- `http://localhost:8000` (fissio-site)
- `http://localhost:3000` (fissio-docs UI)
- `http://localhost:3001` (fissio-crmi)
- `https://fissio.com` (production)
- `https://*.fissio.com` (subdomains)

Edit `superset_config.py` to add more origins.

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

## Workflow

1. **Explore in Jupyter** - Load data, run analysis, prototype visualizations
2. **Build in Superset** - Create production dashboards and charts
3. **Embed everywhere** - Add dashboards to fissio-site, fissio-docs, fissio-crmi, or fissio.com

## Connecting Superset to DuckDB

1. Open Superset at http://localhost:8088
2. Settings → Database Connections → + Database
3. Select "Other" and use SQLAlchemy URI:
   ```
   duckdb:////app/data/fissio.duckdb
   ```

## Sample Notebooks

| Notebook | Description |
|----------|-------------|
| `00_getting_started.ipynb` | DuckDB setup, sample schema, basic queries |

## Nuclear Industry Data Sources

| Source | Data Type | URL |
|--------|-----------|-----|
| NRC | Plant status, inspections | https://www.nrc.gov/reading-rm/doc-collections/ |
| EIA | Generation, capacity | https://www.eia.gov/electricity/data.php |
| IAEA | Global reactor database | https://pris.iaea.org/PRIS/ |
| PJM/ERCOT | Market prices | Various ISO websites |

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
| fissio-base Jupyter | 8888 | http://localhost:8888 |
| fissio-base Superset | 8088 | http://localhost:8088 |

## Tech Stack

- **Database**: DuckDB (analytical SQL)
- **Notebooks**: Jupyter Lab (scipy-notebook)
- **Dashboards**: Apache Superset (with embedding enabled)
- **File Format**: Parquet (columnar, compressed)
- **Container**: Docker Compose

## Production Deployment

For production, update `superset_config.py`:

1. Set `TALISMAN_ENABLED = True`
2. Configure proper CSP headers for your domains
3. Generate a strong `SUPERSET_SECRET_KEY`
4. Enable HTTPS on all services

## License

MIT
