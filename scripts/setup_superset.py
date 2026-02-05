#!/usr/bin/env python3
"""
Set up Superset with DuckDB connection and sample dashboard.

Run inside Superset container:
    docker compose exec superset python /app/data/../scripts/setup_superset.py
"""

import json
import sys

# Superset imports
try:
    from superset import app, db
    from superset.connectors.sqla.models import SqlaTable
    from superset.models.core import Database
    from superset.models.dashboard import Dashboard
    from superset.models.slice import Slice
except ImportError:
    print("Error: Must run inside Superset container")
    sys.exit(1)


def create_database_connection():
    """Create DuckDB database connection."""
    with app.app_context():
        # Check if already exists
        existing = db.session.query(Database).filter_by(database_name="Fissio DuckDB").first()
        if existing:
            print("Database 'Fissio DuckDB' already exists")
            return existing

        database = Database(
            database_name="Fissio DuckDB",
            sqlalchemy_uri="duckdb:////app/data/fissio.duckdb",
            expose_in_sqllab=True,
            allow_run_async=True,
            allow_ctas=False,
            allow_cvas=False,
            extra=json.dumps({
                "allows_virtual_table_explore": True,
            })
        )
        db.session.add(database)
        db.session.commit()
        print(f"Created database connection: {database.database_name}")
        return database


def create_dataset(database, table_name, schema="plants"):
    """Create a dataset from a table."""
    with app.app_context():
        full_name = f"{schema}.{table_name}"

        # Check if exists
        existing = db.session.query(SqlaTable).filter_by(
            table_name=table_name,
            schema=schema,
            database_id=database.id
        ).first()
        if existing:
            print(f"Dataset '{full_name}' already exists")
            return existing

        dataset = SqlaTable(
            table_name=table_name,
            schema=schema,
            database=database,
        )
        db.session.add(dataset)
        db.session.commit()

        # Fetch columns
        dataset.fetch_metadata()
        db.session.commit()

        print(f"Created dataset: {full_name}")
        return dataset


def create_chart(name, viz_type, datasource, params):
    """Create a chart/slice."""
    with app.app_context():
        # Check if exists
        existing = db.session.query(Slice).filter_by(slice_name=name).first()
        if existing:
            print(f"Chart '{name}' already exists")
            return existing

        chart = Slice(
            slice_name=name,
            viz_type=viz_type,
            datasource_type="table",
            datasource_id=datasource.id,
            params=json.dumps(params),
        )
        db.session.add(chart)
        db.session.commit()
        print(f"Created chart: {name}")
        return chart


def create_dashboard(name, slug, charts):
    """Create a dashboard with charts."""
    with app.app_context():
        # Check if exists
        existing = db.session.query(Dashboard).filter_by(slug=slug).first()
        if existing:
            print(f"Dashboard '{name}' already exists")
            return existing

        # Create position JSON for charts
        positions = {
            "DASHBOARD_VERSION_KEY": "v2",
            "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]},
            "GRID_ID": {
                "type": "GRID",
                "id": "GRID_ID",
                "children": [],
                "parents": ["ROOT_ID"]
            },
            "HEADER_ID": {
                "id": "HEADER_ID",
                "type": "HEADER",
                "meta": {"text": name}
            }
        }

        # Add charts to grid
        row_id = "ROW-1"
        positions["GRID_ID"]["children"].append(row_id)
        positions[row_id] = {
            "type": "ROW",
            "id": row_id,
            "children": [],
            "parents": ["ROOT_ID", "GRID_ID"],
            "meta": {"background": "BACKGROUND_TRANSPARENT"}
        }

        for i, chart in enumerate(charts):
            chart_id = f"CHART-{chart.id}"
            positions[row_id]["children"].append(chart_id)
            positions[chart_id] = {
                "type": "CHART",
                "id": chart_id,
                "children": [],
                "parents": ["ROOT_ID", "GRID_ID", row_id],
                "meta": {
                    "width": 4,
                    "height": 50,
                    "chartId": chart.id,
                    "sliceName": chart.slice_name
                }
            }

        dashboard = Dashboard(
            dashboard_title=name,
            slug=slug,
            position_json=json.dumps(positions),
            published=True,
        )
        dashboard.slices = charts
        db.session.add(dashboard)
        db.session.commit()
        print(f"Created dashboard: {name}")
        return dashboard


def main():
    print("=" * 60)
    print("Fissio Superset Setup")
    print("=" * 60)

    # 1. Create database connection
    print("\n[1/4] Creating database connection...")
    database = create_database_connection()

    # 2. Create datasets
    print("\n[2/4] Creating datasets...")
    ds_power_plants = create_dataset(database, "global_power_plants", "plants")
    ds_us_nuclear = create_dataset(database, "us_nuclear_plants", "plants")
    ds_us_summary = create_dataset(database, "us_plants_summary", "plants")

    # 3. Create charts
    print("\n[3/4] Creating charts...")

    # Chart 1: Capacity by Fuel Type (Bar)
    chart1 = create_chart(
        name="Global Capacity by Fuel Type",
        viz_type="echarts_timeseries_bar",
        datasource=ds_power_plants,
        params={
            "datasource": f"{ds_power_plants.id}__table",
            "viz_type": "echarts_timeseries_bar",
            "metrics": [{"label": "Total MW", "expressionType": "SQL", "sqlExpression": "SUM(capacity_mw)"}],
            "groupby": ["primary_fuel"],
            "row_limit": 15,
            "order_desc": True,
            "color_scheme": "supersetColors",
        }
    )

    # Chart 2: Plant Count by Country (Table)
    chart2 = create_chart(
        name="Top Countries by Plant Count",
        viz_type="table",
        datasource=ds_power_plants,
        params={
            "datasource": f"{ds_power_plants.id}__table",
            "viz_type": "table",
            "metrics": [{"label": "Count", "expressionType": "SQL", "sqlExpression": "COUNT(*)"}],
            "groupby": ["country_long"],
            "row_limit": 20,
            "order_desc": True,
        }
    )

    # Chart 3: US Nuclear Plants (Table)
    chart3 = create_chart(
        name="US Nuclear Plants",
        viz_type="table",
        datasource=ds_us_nuclear,
        params={
            "datasource": f"{ds_us_nuclear.id}__table",
            "viz_type": "table",
            "all_columns": ["name", "capacity_mw", "commissioning_year", "owner"],
            "row_limit": 100,
            "order_by_cols": ["capacity_mw"],
            "order_desc": True,
        }
    )

    # 4. Create dashboard
    print("\n[4/4] Creating dashboard...")
    charts = [c for c in [chart1, chart2, chart3] if c is not None]
    dashboard = create_dashboard(
        name="Power Plant Analytics",
        slug="power-plants",
        charts=charts
    )

    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nAccess the dashboard at:")
    print("  http://localhost:8088/superset/dashboard/power-plants/")
    print("\nCredentials: admin / admin")


if __name__ == "__main__":
    main()
