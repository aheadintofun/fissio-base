#!/usr/bin/env python3
"""
Simple Superset setup - just create database connection.
Run via: docker compose exec superset superset shell < /app/scripts/setup_superset_simple.py
"""

import json
from superset import db
from superset.models.core import Database

# Check if already exists
existing = db.session.query(Database).filter_by(database_name="Fissio DuckDB").first()
if existing:
    print("Database 'Fissio DuckDB' already exists, id:", existing.id)
else:
    database = Database(
        database_name="Fissio DuckDB",
        sqlalchemy_uri="duckdb:////app/data/fissio.duckdb",
        expose_in_sqllab=True,
        allow_run_async=True,
        allow_ctas=False,
        allow_cvas=False,
    )
    db.session.add(database)
    db.session.commit()
    print("Created database 'Fissio DuckDB', id:", database.id)

print("\nDone! Now go to Superset and:")
print("1. Go to Data > Datasets > + Dataset")
print("2. Select 'Fissio DuckDB' database")
print("3. Select 'plants' schema")
print("4. Select 'global_power_plants' table")
print("5. Create charts from the dataset")
