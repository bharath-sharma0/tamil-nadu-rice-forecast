WITH source_names AS (
    SELECT DISTINCT district_name
    FROM rice_yield_staging
)
SELECT
    LOWER(TRIM(district_name)) AS district_key,
    COUNT(*) AS source_name_count,
    GROUP_CONCAT(district_name, ' | ') AS source_names
FROM source_names
GROUP BY district_key
HAVING COUNT(*) > 1 OR district_key = ''
ORDER BY district_key;
