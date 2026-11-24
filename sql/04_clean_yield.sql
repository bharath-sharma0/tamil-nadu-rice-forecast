DROP VIEW IF EXISTS rice_yield_clean;

CREATE VIEW rice_yield_clean AS
SELECT
    district_name,
    crop_year_start,
    area_ha,
    production_tonnes,
    reported_yield_tonnes_per_ha,
    CASE
        WHEN area_ha > 0 AND production_tonnes >= 0
        THEN 1000.0 * production_tonnes / area_ha
    END AS yield_kg_per_ha,
    CASE
        WHEN area_ha IS NULL AND production_tonnes IS NULL
             AND reported_yield_tonnes_per_ha IS NULL THEN 'entirely blank'
        WHEN area_ha IS NULL OR area_ha <= 0
             OR production_tonnes IS NULL OR production_tonnes < 0
             THEN 'cannot derive yield'
        WHEN production_tonnes = 0 THEN 'zero production'
        WHEN reported_yield_tonnes_per_ha = 0 THEN 'positive production, reported zero yield'
        ELSE 'derived from area and production'
    END AS quality_status
FROM rice_yield_staging;
