CREATE TABLE IF NOT EXISTS rice_yield_staging (
    district_name TEXT NOT NULL,
    crop_year_start INTEGER NOT NULL,
    area_ha REAL,
    production_tonnes REAL,
    reported_yield_tonnes_per_ha REAL,
    PRIMARY KEY (district_name, crop_year_start)
);
