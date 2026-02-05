#!/usr/bin/env python3
"""Create datasets and charts in Superset."""

import json
from superset import db
from superset.connectors.sqla.models import SqlaTable
from superset.models.core import Database
from superset.models.slice import Slice
from superset.models.dashboard import Dashboard

# Get database
database = db.session.query(Database).filter_by(database_name="Fissio DuckDB").first()
if not database:
    print("ERROR: Database 'Fissio DuckDB' not found. Run setup_superset_simple.py first.")
    exit(1)

print(f"Using database: {database.database_name} (id={database.id})")

# Create datasets
def get_or_create_dataset(table_name, schema="plants"):
    existing = db.session.query(SqlaTable).filter_by(
        table_name=table_name, schema=schema, database_id=database.id
    ).first()
    if existing:
        print(f"Dataset '{schema}.{table_name}' already exists (id={existing.id})")
        return existing

    dataset = SqlaTable(table_name=table_name, schema=schema, database_id=database.id)
    db.session.add(dataset)
    db.session.commit()

    # Fetch columns
    try:
        dataset.fetch_metadata()
        db.session.commit()
    except Exception as e:
        print(f"Warning: Could not fetch metadata: {e}")

    print(f"Created dataset '{schema}.{table_name}' (id={dataset.id})")
    return dataset

ds_plants = get_or_create_dataset("global_power_plants")
ds_nuclear = get_or_create_dataset("us_nuclear_plants")
ds_summary = get_or_create_dataset("us_plants_summary")

# Create chart
def get_or_create_chart(name, viz_type, datasource_id, params):
    existing = db.session.query(Slice).filter_by(slice_name=name).first()
    if existing:
        print(f"Chart '{name}' already exists (id={existing.id})")
        return existing

    chart = Slice(
        slice_name=name,
        viz_type=viz_type,
        datasource_type="table",
        datasource_id=datasource_id,
        params=json.dumps(params),
    )
    db.session.add(chart)
    db.session.commit()
    print(f"Created chart '{name}' (id={chart.id})")
    return chart

# Chart 1: Capacity by Fuel Type
chart1 = get_or_create_chart(
    "Global Capacity by Fuel Type",
    "dist_bar",
    ds_plants.id,
    {
        "metrics": ["SUM(capacity_mw)"],
        "groupby": ["primary_fuel"],
        "row_limit": 15,
        "color_scheme": "supersetColors",
        "show_legend": True,
        "y_axis_format": "SMART_NUMBER",
    }
)

# Chart 2: Top Countries
chart2 = get_or_create_chart(
    "Top 20 Countries by Capacity",
    "dist_bar",
    ds_plants.id,
    {
        "metrics": ["SUM(capacity_mw)"],
        "groupby": ["country_long"],
        "row_limit": 20,
        "color_scheme": "supersetColors",
        "show_legend": False,
        "y_axis_format": "SMART_NUMBER",
    }
)

# Chart 3: US Nuclear Table
chart3 = get_or_create_chart(
    "US Nuclear Plants",
    "table",
    ds_nuclear.id,
    {
        "all_columns": ["name", "capacity_mw", "commissioning_year", "owner"],
        "row_limit": 100,
        "page_length": 25,
    }
)

# Chart 4: Fuel Summary Pie
chart4 = get_or_create_chart(
    "US Capacity by Fuel",
    "pie",
    ds_summary.id,
    {
        "metrics": ["SUM(total_capacity_mw)"],
        "groupby": ["primary_fuel"],
        "row_limit": 15,
        "color_scheme": "supersetColors",
        "show_legend": True,
        "show_labels": True,
    }
)

# Create dashboard
existing_dash = db.session.query(Dashboard).filter_by(slug="power-plants").first()
if existing_dash:
    print(f"Dashboard 'power-plants' already exists (id={existing_dash.id})")
else:
    position = {
        "DASHBOARD_VERSION_KEY": "v2",
        "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]},
        "GRID_ID": {"type": "GRID", "id": "GRID_ID", "children": ["ROW-1", "ROW-2"], "parents": ["ROOT_ID"]},
        "HEADER_ID": {"id": "HEADER_ID", "type": "HEADER", "meta": {"text": "Power Plant Analytics"}},
        "ROW-1": {
            "type": "ROW", "id": "ROW-1",
            "children": [f"CHART-{chart1.id}", f"CHART-{chart4.id}"],
            "parents": ["ROOT_ID", "GRID_ID"],
            "meta": {"background": "BACKGROUND_TRANSPARENT"}
        },
        "ROW-2": {
            "type": "ROW", "id": "ROW-2",
            "children": [f"CHART-{chart2.id}", f"CHART-{chart3.id}"],
            "parents": ["ROOT_ID", "GRID_ID"],
            "meta": {"background": "BACKGROUND_TRANSPARENT"}
        },
    }
    # Add chart positions
    for chart in [chart1, chart2, chart3, chart4]:
        cid = f"CHART-{chart.id}"
        row = "ROW-1" if chart in [chart1, chart4] else "ROW-2"
        position[cid] = {
            "type": "CHART", "id": cid, "children": [],
            "parents": ["ROOT_ID", "GRID_ID", row],
            "meta": {"width": 6, "height": 50, "chartId": chart.id, "sliceName": chart.slice_name}
        }

    dashboard = Dashboard(
        dashboard_title="Power Plant Analytics",
        slug="power-plants",
        position_json=json.dumps(position),
        published=True,
    )
    dashboard.slices = [chart1, chart2, chart3, chart4]
    db.session.add(dashboard)
    db.session.commit()
    print(f"Created dashboard 'Power Plant Analytics' (id={dashboard.id})")

print("\n" + "="*60)
print("Setup Complete!")
print("="*60)
print("\nView dashboard: http://localhost:8088/superset/dashboard/power-plants/")
print("Login: admin / admin")
