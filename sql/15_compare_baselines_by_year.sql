SELECT
    y.crop_year_start,
    COUNT(*) AS shared_rows,
    AVG(ABS(y.yield_kg_per_ha - l.baseline_last_available)) AS last_mae,
    AVG(ABS(y.yield_kg_per_ha - a.baseline_avg_3)) AS average_mae
FROM fact_kharif_rice_yield AS y
JOIN rice_yield_last_available AS l USING (district_id, crop_year_start)
JOIN rice_yield_trailing_average AS a USING (district_id, crop_year_start)
WHERE y.crop_year_start BETWEEN :first_year AND :last_year
  AND y.yield_kg_per_ha IS NOT NULL
  AND l.baseline_last_available IS NOT NULL
  AND a.baseline_avg_3 IS NOT NULL
GROUP BY y.crop_year_start
ORDER BY y.crop_year_start;
