#!/usr/bin/env python3
"""
Seed DuckDB with power industry data sources.

Data Sources:
- WRI Global Power Plant Database (CSV)
- EIA Form 860 (plant characteristics)
- EIA Form 923 (generation and fuel)
- NRC Reactor Status (daily updates)
"""

import duckdb
import urllib.request
import os
from pathlib import Path

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "fissio.duckdb"

# Data source URLs
SOURCES = {
    "wri_power_plants": {
        "url": "https://raw.githubusercontent.com/wri/global-power-plant-database/master/output_database/global_power_plant_database.csv",
        "description": "WRI Global Power Plant Database v1.3.0"
    },
    "nrc_reactor_status": {
        "url": "https://www.nrc.gov/reading-rm/doc-collections/event-status/reactor-status/PowerReactorStatusForLast365Days.txt",
        "description": "NRC Power Reactor Status (Last 365 Days)"
    },
    "eia_860_plants": {
        "url": "https://raw.githubusercontent.com/catalyst-cooperative/pudl/main/src/pudl/package_data/eia860/plant_info_eia.csv",
        "description": "EIA-860 Plant Information (via PUDL)"
    },
    "eia_923_generation": {
        "url": "https://www.eia.gov/electricity/data/state/generation_annual.xlsx",
        "description": "EIA Annual Generation by State (Excel)"
    }
}


def download_file(url: str, dest: Path) -> bool:
    """Download a file from URL to destination."""
    print(f"  Downloading: {url}")
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"  Saved to: {dest}")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def seed_wri_power_plants(con: duckdb.DuckDBPyConnection):
    """Load WRI Global Power Plant Database."""
    print("\n[1/4] WRI Global Power Plant Database")

    csv_path = DATA_DIR / "wri_power_plants.csv"
    if not csv_path.exists():
        if not download_file(SOURCES["wri_power_plants"]["url"], csv_path):
            return

    con.execute("CREATE SCHEMA IF NOT EXISTS plants")
    con.execute("DROP TABLE IF EXISTS plants.global_power_plants")
    con.execute(f"""
        CREATE TABLE plants.global_power_plants AS
        SELECT
            country,
            country_long,
            name,
            gppd_idnr as plant_id,
            capacity_mw,
            latitude,
            longitude,
            primary_fuel,
            other_fuel1,
            other_fuel2,
            other_fuel3,
            commissioning_year,
            owner,
            source,
            url,
            geolocation_source,
            wepp_id,
            year_of_capacity_data,
            generation_gwh_2013,
            generation_gwh_2014,
            generation_gwh_2015,
            generation_gwh_2016,
            generation_gwh_2017,
            generation_data_source,
            estimated_generation_gwh_2013,
            estimated_generation_gwh_2014,
            estimated_generation_gwh_2015,
            estimated_generation_gwh_2016,
            estimated_generation_gwh_2017
        FROM read_csv('{csv_path}', auto_detect=true)
    """)

    count = con.execute("SELECT COUNT(*) FROM plants.global_power_plants").fetchone()[0]
    print(f"  Loaded {count:,} power plants")

    # Summary by fuel type
    print("\n  Summary by primary fuel:")
    summary = con.execute("""
        SELECT primary_fuel, COUNT(*) as count, ROUND(SUM(capacity_mw), 0) as total_mw
        FROM plants.global_power_plants
        GROUP BY primary_fuel
        ORDER BY total_mw DESC
        LIMIT 10
    """).fetchall()
    for fuel, cnt, mw in summary:
        print(f"    {fuel}: {cnt:,} plants, {mw:,.0f} MW")


def seed_nrc_reactor_status(con: duckdb.DuckDBPyConnection):
    """Load NRC Power Reactor Status."""
    print("\n[2/4] NRC Power Reactor Status")

    txt_path = DATA_DIR / "nrc_reactor_status.txt"
    if not txt_path.exists():
        if not download_file(SOURCES["nrc_reactor_status"]["url"], txt_path):
            return

    con.execute("CREATE SCHEMA IF NOT EXISTS regulatory")
    con.execute("DROP TABLE IF EXISTS regulatory.nrc_reactor_status")

    # NRC file is pipe-delimited
    con.execute(f"""
        CREATE TABLE regulatory.nrc_reactor_status AS
        SELECT *
        FROM read_csv('{txt_path}',
            delim='|',
            header=true,
            auto_detect=true,
            ignore_errors=true
        )
    """)

    count = con.execute("SELECT COUNT(*) FROM regulatory.nrc_reactor_status").fetchone()[0]
    print(f"  Loaded {count:,} reactor status records")


def seed_eia_860(con: duckdb.DuckDBPyConnection):
    """Load EIA-860 plant data."""
    print("\n[3/4] EIA Form 860 (Plant Information)")

    # Try PUDL's processed CSV first
    csv_path = DATA_DIR / "eia_860_plants.csv"

    # For now, create a simplified US nuclear plants table from WRI data
    con.execute("""
        CREATE OR REPLACE TABLE plants.us_nuclear_plants AS
        SELECT
            name,
            plant_id,
            capacity_mw,
            latitude,
            longitude,
            commissioning_year,
            owner
        FROM plants.global_power_plants
        WHERE country = 'USA' AND primary_fuel = 'Nuclear'
        ORDER BY capacity_mw DESC
    """)

    count = con.execute("SELECT COUNT(*) FROM plants.us_nuclear_plants").fetchone()[0]
    print(f"  Created plants.us_nuclear_plants with {count} US nuclear plants (from WRI)")

    # Create US plants by fuel type
    con.execute("""
        CREATE OR REPLACE TABLE plants.us_plants_summary AS
        SELECT
            primary_fuel,
            COUNT(*) as plant_count,
            ROUND(SUM(capacity_mw), 0) as total_capacity_mw,
            ROUND(AVG(capacity_mw), 1) as avg_capacity_mw
        FROM plants.global_power_plants
        WHERE country = 'USA'
        GROUP BY primary_fuel
        ORDER BY total_capacity_mw DESC
    """)
    print("  Created plants.us_plants_summary")


def seed_eia_923(con: duckdb.DuckDBPyConnection):
    """Load EIA-923 generation data."""
    print("\n[4/4] EIA Form 923 (Generation)")

    # Create market schema for generation data
    con.execute("CREATE SCHEMA IF NOT EXISTS market")

    # For now, create a summary view from WRI generation estimates
    con.execute("""
        CREATE OR REPLACE TABLE market.generation_summary AS
        SELECT
            country,
            primary_fuel,
            COUNT(*) as plant_count,
            ROUND(SUM(capacity_mw), 0) as total_capacity_mw,
            ROUND(SUM(COALESCE(generation_gwh_2017, estimated_generation_gwh_2017, 0)), 0) as generation_gwh_2017
        FROM plants.global_power_plants
        GROUP BY country, primary_fuel
        ORDER BY generation_gwh_2017 DESC
    """)

    count = con.execute("SELECT COUNT(*) FROM market.generation_summary").fetchone()[0]
    print(f"  Created market.generation_summary with {count} rows")


def create_views(con: duckdb.DuckDBPyConnection):
    """Create useful views for analysis."""
    print("\n[Views] Creating analysis views")

    # US power plants view
    con.execute("""
        CREATE OR REPLACE VIEW plants.v_us_power_plants AS
        SELECT *
        FROM plants.global_power_plants
        WHERE country = 'USA'
    """)
    print("  Created plants.v_us_power_plants")

    # Nuclear plants worldwide view
    con.execute("""
        CREATE OR REPLACE VIEW plants.v_nuclear_plants AS
        SELECT *
        FROM plants.global_power_plants
        WHERE primary_fuel = 'Nuclear'
    """)
    print("  Created plants.v_nuclear_plants")


def export_parquet(con: duckdb.DuckDBPyConnection):
    """Export key tables to Parquet for Superset."""
    print("\n[Export] Creating Parquet files for Superset")

    exports = [
        ("plants.global_power_plants", "global_power_plants.parquet"),
        ("plants.us_nuclear_plants", "us_nuclear_plants.parquet"),
        ("plants.us_plants_summary", "us_plants_summary.parquet"),
    ]

    for table, filename in exports:
        path = DATA_DIR / filename
        con.execute(f"COPY {table} TO '{path}' (FORMAT PARQUET)")
        print(f"  Exported {table} -> {filename}")


def main():
    print("=" * 60)
    print("Fissio Base - Data Seeding Script")
    print("=" * 60)

    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)

    # Connect to DuckDB
    print(f"\nConnecting to: {DB_PATH}")
    con = duckdb.connect(str(DB_PATH))

    # Install and load extensions
    con.execute("INSTALL httpfs")
    con.execute("LOAD httpfs")

    # Seed each data source
    seed_wri_power_plants(con)
    seed_nrc_reactor_status(con)
    seed_eia_860(con)
    seed_eia_923(con)

    # Create views
    create_views(con)

    # Export to Parquet
    export_parquet(con)

    # Summary
    print("\n" + "=" * 60)
    print("Seeding Complete!")
    print("=" * 60)

    print("\nSchemas:")
    schemas = con.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'main')").fetchall()
    for (schema,) in schemas:
        print(f"  - {schema}")

    print("\nTables:")
    tables = con.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema IN ('plants', 'regulatory', 'market')
        ORDER BY table_schema, table_name
    """).fetchall()
    for schema, table in tables:
        count = con.execute(f"SELECT COUNT(*) FROM {schema}.{table}").fetchone()[0]
        print(f"  - {schema}.{table} ({count:,} rows)")

    print("\nViews:")
    views = con.execute("""
        SELECT table_schema, table_name
        FROM information_schema.views
        WHERE table_schema IN ('plants', 'regulatory', 'market')
    """).fetchall()
    for schema, view in views:
        print(f"  - {schema}.{view}")

    print("\nParquet exports:")
    for f in DATA_DIR.glob("*.parquet"):
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  - {f.name} ({size_mb:.1f} MB)")

    con.close()
    print("\nDone! Open http://localhost:8080 to explore the data.")


if __name__ == "__main__":
    main()
