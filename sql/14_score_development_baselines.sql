WITH observed AS (
    SELECT
        y.yield_kg_per_ha AS actual,
        l.baseline_last_available AS last_available,
        a.baseline_avg_3 AS trailing_average
    FROM fact_kharif_rice_yield AS y
    JOIN rice_yield_last_available AS l USING (district_id, crop_year_start)
    JOIN rice_yield_trailing_average AS a USING (district_id, crop_year_start)
    WHERE y.crop_year_start BETWEEN :first_year AND :last_year
      AND y.yield_kg_per_ha IS NOT NULL
)
SELECT
    COUNT(*),
    COUNT(last_available),
    COUNT(trailing_average),
    COUNT(CASE WHEN last_available IS NOT NULL
                AND trailing_average IS NOT NULL THEN 1 END),
    AVG(CASE WHEN trailing_average IS NOT NULL
             THEN ABS(actual - last_available) END),
    AVG(CASE WHEN last_available IS NOT NULL
             THEN ABS(actual - trailing_average) END)
FROM observed;
