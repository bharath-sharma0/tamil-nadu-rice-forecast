WITH classified AS (
    SELECT
        CASE
            WHEN area_ha IS NULL
             AND production_tonnes IS NULL
             AND reported_yield_tonnes_per_ha IS NULL THEN 'entirely blank'
            WHEN area_ha > 0
             AND production_tonnes > 0
             AND reported_yield_tonnes_per_ha > 0 THEN 'positive values'
            ELSE 'needs review'
        END AS status
    FROM rice_yield_staging
)
SELECT status, COUNT(*) AS district_years
FROM classified
GROUP BY status
ORDER BY status;
