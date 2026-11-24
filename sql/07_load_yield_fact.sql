BEGIN;

CREATE TABLE IF NOT EXISTS fact_kharif_rice_yield (
    district_id INTEGER NOT NULL REFERENCES dim_district(district_id),
    crop_year_start INTEGER NOT NULL,
    area_ha REAL,
    production_tonnes REAL,
    yield_kg_per_ha REAL CHECK (yield_kg_per_ha >= 0),
    quality_status TEXT NOT NULL,
    PRIMARY KEY (district_id, crop_year_start)
);

CREATE INDEX IF NOT EXISTS idx_kharif_rice_yield_year
    ON fact_kharif_rice_yield (crop_year_start);

DELETE FROM fact_kharif_rice_yield;

INSERT INTO fact_kharif_rice_yield (
    district_id, crop_year_start, area_ha, production_tonnes,
    yield_kg_per_ha, quality_status
)
SELECT d.district_id, y.crop_year_start, y.area_ha, y.production_tonnes,
       y.yield_kg_per_ha, y.quality_status
FROM rice_yield_clean AS y
JOIN dim_district AS d ON d.district_key = LOWER(TRIM(y.district_name));
