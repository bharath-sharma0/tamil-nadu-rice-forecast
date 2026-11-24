DROP VIEW IF EXISTS rice_yield_trailing_average;

CREATE VIEW rice_yield_trailing_average AS
WITH history AS (
    SELECT
        district_id,
        crop_year_start,
        COUNT(yield_kg_per_ha) OVER eligible AS observed_seasons,
        AVG(yield_kg_per_ha) OVER eligible AS average_yield,
        MIN(crop_year_start) OVER eligible AS first_year,
        MAX(crop_year_start) OVER eligible AS last_year
    FROM fact_kharif_rice_yield
    WINDOW eligible AS (
        PARTITION BY district_id ORDER BY crop_year_start
        ROWS BETWEEN 4 PRECEDING AND 2 PRECEDING
    )
)
SELECT
    district_id,
    crop_year_start,
    CASE WHEN observed_seasons = 3 THEN average_yield END AS baseline_avg_3,
    CASE WHEN observed_seasons = 3 THEN first_year END AS first_source_year,
    CASE WHEN observed_seasons = 3 THEN last_year END AS last_source_year
FROM history;
