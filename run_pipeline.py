import argparse
import json
import sqlite3
import subprocess
import sys
from contextlib import closing
from pathlib import Path

from src.download_weather import prepare_weather_inputs
from src.frozen_forecasts import generate_frozen_forecasts
from src.score_forecasts import write_test_reports

ROOT = Path(__file__).resolve().parent


def run_pipeline(raw_dir, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    database = output_dir / "rice_forecast.sqlite"
    plan = json.loads(
        (ROOT / "reports" / "frozen_evaluation_plan.json").read_text(encoding="utf-8")
    )

    subprocess.run(
        [sys.executable, str(ROOT / "src" / "build_database.py"),
         "--raw", str(raw_dir), "--output", str(database)],
        check=True,
    )

    with closing(sqlite3.connect(database)) as conn:
        print("Generating frozen forecasts...", flush=True)
        forecasts = generate_frozen_forecasts(conn, plan)
        district_names = dict(conn.execute(
            "SELECT district_id, district_name FROM dim_district"
        ))
        years = plan["final_test_years"]
        actuals = {
            (district, year): value
            for district, year, value in conn.execute(
                """SELECT district_id, crop_year_start, yield_kg_per_ha
                   FROM fact_kharif_rice_yield
                   WHERE crop_year_start BETWEEN ? AND ?
                     AND yield_kg_per_ha IS NOT NULL""",
                (min(years), max(years)),
            )
        }

    metrics_count, interval_count = write_test_reports(
        output_dir, plan, district_names, actuals, forecasts
    )
    print(f"Saved {metrics_count} metric rows and {interval_count} interval rows")
    print(f"Outputs: {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rebuild and reproduce the frozen rice forecast evaluation")
    parser.add_argument("--raw", type=Path, default=ROOT / "data" / "raw")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "processed")
    parser.add_argument(
        "--download-weather", action="store_true",
        help="Download missing boundary and NASA weather inputs",
    )
    args = parser.parse_args()
    if args.download_weather:
        prepare_weather_inputs(args.raw)
    run_pipeline(args.raw, args.output_dir)
