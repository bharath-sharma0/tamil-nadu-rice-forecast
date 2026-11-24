"""Export the frozen forecast results for a local Power BI report."""

import csv
import json
import shutil
import sqlite3
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"


def write_table(connection, output, filename, query, parameters=()):
    cursor = connection.execute(query, parameters)
    rows = cursor.fetchall()
    with (output / filename).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([column[0] for column in cursor.description])
        writer.writerows(rows)
    return len(rows)


def export():
    database = DATA / "rice_forecast.sqlite"
    plan = json.loads((REPORTS / "frozen_evaluation_plan.json").read_text(encoding="utf-8"))
    years = plan["final_test_years"]
    width = plan["prediction_interval"]["half_width_kg_per_ha"]
    output = DATA / "powerbi"
    output.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as conn:
        forecasts = write_table(
            conn, output, "district_forecasts.csv",
            """
            SELECT d.district_name AS district,
                   y.crop_year_start AS crop_year,
                   y.yield_kg_per_ha AS actual_yield_kg_ha,
                   a.baseline_avg_3 AS forecast_yield_kg_ha,
                   MAX(0, a.baseline_avg_3 - :width) AS lower_kg_ha,
                   a.baseline_avg_3 + :width AS upper_kg_ha,
                   CASE WHEN a.baseline_avg_3 IS NULL THEN 'Insufficient history'
                        ELSE 'Forecast available' END AS forecast_status
            FROM fact_kharif_rice_yield AS y
            JOIN dim_district AS d USING (district_id)
            JOIN rice_yield_trailing_average AS a USING (district_id, crop_year_start)
            WHERE y.crop_year_start BETWEEN :start AND :end
            ORDER BY district, crop_year
            """, {"width": width, "start": min(years), "end": max(years)},
        )
        history = write_table(
            conn, output, "district_history.csv",
            """
            SELECT d.district_name AS district, y.crop_year_start AS crop_year,
                   y.yield_kg_per_ha AS observed_yield_kg_ha
            FROM fact_kharif_rice_yield AS y
            JOIN dim_district AS d USING (district_id)
            ORDER BY district, crop_year
            """,
        )
    shutil.copyfile(REPORTS / "final_test_metrics.csv", output / "model_metrics.csv")
    print(f"Exported {forecasts} forecast rows and {history} history rows to {output}")


if __name__ == "__main__":
    export()
