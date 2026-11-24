import re
from html import unescape


def parse_yield_export(raw_file):
    report = raw_file.read_text(encoding="utf-8-sig")
    years = [
        int(year)
        for year in re.findall(r"<th\b[^>]*>\s*(\d{4})\s*-\s*\d{4}\s*</th>", report)
    ]
    if years != list(range(1998, 2023)):
        raise ValueError(f"Unexpected crop-year headers: {years}")

    records = []
    for row in re.findall(r"<tr\b[^>]*>(.*?)</tr>", report, flags=re.S):
        cells = [
            unescape(re.sub(r"<[^>]+>", "", cell)).strip()
            for cell in re.findall(r"<td\b[^>]*>(.*?)</td>", row, flags=re.S)
        ]
        if not cells:
            continue
        if len(cells) != 3 + 3 * len(years) or cells[1] != "Tamil Nadu" or not cells[2]:
            raise ValueError("Unexpected district row in the yield export")

        for index, year in enumerate(years):
            offset = 3 + 3 * index
            measurements = [
                float(value.replace(",", "")) if value else None
                for value in cells[offset:offset + 3]
            ]
            records.append((cells[2], year, *measurements))

    keys = {(district, year) for district, year, *_ in records}
    if len(keys) != len(records) or len({district for district, _ in keys}) != 38:
        raise ValueError("Duplicate district-years or unexpected district count")
    return records


def load_yield(conn, raw_file, sql_dir):
    records = parse_yield_export(raw_file)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute((sql_dir / "01_create_staging.sql").read_text(encoding="utf-8"))
    with conn:
        conn.execute("DELETE FROM rice_yield_staging")
        conn.executemany(
            "INSERT INTO rice_yield_staging VALUES (?, ?, ?, ?, ?)", records
        )

    for filename in (
        "04_clean_yield.sql",
        "06_create_district_dimension.sql",
        "07_load_yield_fact.sql",
    ):
        with conn:
            conn.executescript((sql_dir / filename).read_text(encoding="utf-8"))

    return conn.execute(
        "SELECT COUNT(*), COUNT(yield_kg_per_ha) FROM fact_kharif_rice_yield"
    ).fetchone()
