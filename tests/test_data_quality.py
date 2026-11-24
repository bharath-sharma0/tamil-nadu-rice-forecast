import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from src.yield_ingest import parse_yield_export

ROOT = Path(__file__).resolve().parents[1]


class DataQualityTest(unittest.TestCase):
    def test_export_with_missing_year_headers_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            raw_file = Path(folder) / "bad_export.xls"
            raw_file.write_text("<table></table>", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "crop-year headers"):
                parse_yield_export(raw_file)

    def test_cutoff_audit_flags_late_weather_and_yield(self):
        audit_sql = (ROOT / "sql" / "22_check_feature_cutoffs.sql").read_text(encoding="utf-8")
        with closing(sqlite3.connect(":memory:")) as conn:
            conn.execute(
                """CREATE TABLE rice_forecast_features (
                    crop_year_start INTEGER,
                    latest_weather_date TEXT,
                    yield_last_available REAL,
                    last_yield_source_year INTEGER,
                    yield_trailing_avg_3 REAL,
                    average_first_source_year INTEGER,
                    average_last_source_year INTEGER
                )"""
            )
            conn.execute(
                "INSERT INTO rice_forecast_features VALUES (?, ?, ?, ?, ?, ?, ?)",
                (2020, "2020-07-31", 3500, 2018, 3300, 2016, 2018),
            )
            self.assertEqual(conn.execute(audit_sql).fetchone(), (1, 0, 0))

            conn.execute(
                "INSERT INTO rice_forecast_features VALUES (?, ?, ?, ?, ?, ?, ?)",
                (2020, "2020-08-01", 3500, 2019, 3300, 2017, 2019),
            )
            self.assertEqual(conn.execute(audit_sql).fetchone(), (2, 1, 1))
