CREATE TABLE IF NOT EXISTS dim_district (
    district_id INTEGER PRIMARY KEY,
    district_key TEXT NOT NULL UNIQUE CHECK (district_key <> ''),
    district_name TEXT NOT NULL
);

INSERT INTO dim_district (district_key, district_name)
SELECT DISTINCT LOWER(TRIM(district_name)), district_name
FROM rice_yield_staging
ORDER BY 1
ON CONFLICT (district_key) DO UPDATE
SET district_name = excluded.district_name;
