import json
from datetime import date, timedelta


def iter_weather_rows(raw_dir, cells):
    start, end = date(1998, 1, 1), date(2022, 7, 31)
    dates = {
        day.strftime("%Y%m%d"): day.isoformat()
        for offset in range((end - start).days + 1)
        for day in [start + timedelta(days=offset)]
    }

    for lon, lat in sorted(cells):
        path = raw_dir / "nasa_power" / f"lon_{lon:.3f}_lat_{lat:.3f}.json"
        weather = json.loads(path.read_bytes())
        header = weather["header"]
        values = weather["properties"]["parameter"]

        if tuple(weather["geometry"]["coordinates"][:2]) != (lon, lat):
            raise ValueError(f"Unexpected grid center in {path.name}")
        if header["time_standard"] != "LST":
            raise ValueError(f"Unexpected time standard in {path.name}")

        for parameter, unit in (("T2M", "C"), ("PRECTOTCORR", "mm/day")):
            if set(values[parameter]) != dates.keys():
                raise ValueError(f"Date mismatch for {parameter} in {path.name}")
            if weather["parameters"][parameter]["units"] != unit:
                raise ValueError(f"Unit mismatch for {parameter} in {path.name}")

        missing = header["fill_value"]
        for day, iso_date in dates.items():
            temperature = values["T2M"][day]
            rainfall = values["PRECTOTCORR"][day]
            yield (
                lon, lat, iso_date,
                None if temperature == missing else temperature,
                None if rainfall == missing else rainfall,
            )


def load_weather(conn, raw_dir, sql_dir, points, cells):
    for filename in ("17_create_daily_weather.sql", "18_create_district_weather_map.sql"):
        conn.execute((sql_dir / filename).read_text(encoding="utf-8"))

    district_ids = dict(conn.execute("SELECT district_name, district_id FROM dim_district"))
    mapping = [
        (district_ids[name], *points[name], lon, lat)
        for (lon, lat), names in cells.items()
        for name in names
    ]
    if len(mapping) != len(district_ids) or set(points) != set(district_ids):
        raise ValueError("Weather mapping does not cover the district dimension")

    with conn:
        conn.execute("DELETE FROM district_weather_map")
        conn.execute("DELETE FROM fact_weather_daily")
        conn.executemany(
            "INSERT INTO fact_weather_daily VALUES (?, ?, ?, ?, ?)",
            iter_weather_rows(raw_dir, cells),
        )
        conn.executemany(
            "INSERT INTO district_weather_map VALUES (?, ?, ?, ?, ?)", mapping
        )

    for filename in (
        "10_last_available_yield.sql",
        "11_trailing_yield_average.sql",
        "19_build_monthly_weather.sql",
        "20_build_weather_features.sql",
        "21_join_forecast_features.sql",
    ):
        conn.executescript((sql_dir / filename).read_text(encoding="utf-8"))
