import argparse
import sqlite3
from contextlib import closing
from pathlib import Path
from tempfile import NamedTemporaryFile

from weather_ingest import build_weather_mapping
from weather_load import load_weather
from yield_ingest import load_yield

ROOT = Path(__file__).resolve().parents[1]


def build_database(raw_dir, sql_dir, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(dir=destination.parent, suffix=".sqlite", delete=False) as handle:
        temporary = Path(handle.name)

    try:
        with closing(sqlite3.connect(temporary)) as conn:
            yield_counts = load_yield(conn, raw_dir / "apy_query_report.xls", sql_dir)
            names = [name for (name,) in conn.execute(
                "SELECT district_name FROM dim_district"
            )]
            points, cells = build_weather_mapping(raw_dir, names)
            load_weather(conn, raw_dir, sql_dir, points, cells)

            daily_count = conn.execute(
                "SELECT COUNT(*) FROM fact_weather_daily"
            ).fetchone()[0]
            cutoff_audit = conn.execute(
                (sql_dir / "22_check_feature_cutoffs.sql").read_text(encoding="utf-8")
            ).fetchone()
            if yield_counts != (950, 767) or daily_count != 296_274:
                raise ValueError("Rebuilt data counts differ from the verified inputs")
            if cutoff_audit != (950, 0, 0):
                raise ValueError(f"Feature cutoff audit failed: {cutoff_audit}")

        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)

    print(f"Yield: {yield_counts[0]} rows | Weather: {daily_count:,} daily rows")
    print(f"Cutoff audit: {cutoff_audit[0]} rows | Weather {cutoff_audit[1]} | Yield {cutoff_audit[2]}")
    print(f"Database ready: {destination.name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rebuild the rice forecast SQLite database")
    parser.add_argument("--raw", type=Path, default=ROOT / "data" / "raw")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "data" / "processed" / "rice_forecast.sqlite")
    args = parser.parse_args()
    build_database(args.raw, ROOT / "sql", args.output)
