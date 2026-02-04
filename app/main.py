"""Fissio Base - Central Analytics Platform Frontend"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

app = FastAPI(title="Fissio Base", description="Central Analytics & Dashboard Platform")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Service URLs (can be overridden by environment)
JUPYTER_URL = os.getenv("JUPYTER_URL", "http://localhost:8888")
SUPERSET_URL = os.getenv("SUPERSET_URL", "http://localhost:8088")
DUCKDB_URL = os.getenv("DUCKDB_URL", "http://localhost:5522")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home dashboard with links to all services."""
    return templates.TemplateResponse("home.html", {
        "request": request,
        "jupyter_url": JUPYTER_URL,
        "superset_url": SUPERSET_URL,
        "duckdb_url": DUCKDB_URL,
    })


@app.get("/jupyter", response_class=HTMLResponse)
async def jupyter(request: Request):
    """Embedded Jupyter Lab view."""
    return templates.TemplateResponse("jupyter.html", {
        "request": request,
        "jupyter_url": JUPYTER_URL,
        "superset_url": SUPERSET_URL,
        "duckdb_url": DUCKDB_URL,
    })


@app.get("/superset", response_class=HTMLResponse)
async def superset(request: Request):
    """Embedded Superset view."""
    return templates.TemplateResponse("superset.html", {
        "request": request,
        "jupyter_url": JUPYTER_URL,
        "superset_url": SUPERSET_URL,
        "duckdb_url": DUCKDB_URL,
    })


@app.get("/duckdb", response_class=HTMLResponse)
async def duckdb(request: Request):
    """Embedded DuckDB UI view."""
    return templates.TemplateResponse("duckdb.html", {
        "request": request,
        "jupyter_url": JUPYTER_URL,
        "superset_url": SUPERSET_URL,
        "duckdb_url": DUCKDB_URL,
    })


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "fissio-base"}
