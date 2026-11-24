WITH expected AS (
    SELECT f.yield_lag_1, f.yield_avg_prior_3,
           y1.yield_kg_per_ha AS expected_lag,
           (y1.yield_kg_per_ha + y2.yield_kg_per_ha + y3.yield_kg_per_ha)
               / 3.0 AS expected_avg
    FROM rice_yield_history_features AS f
    LEFT JOIN fact_kharif_rice_yield AS y1
      ON y1.district_id = f.district_id
     AND y1.crop_year_start = f.crop_year_start - 1
    LEFT JOIN fact_kharif_rice_yield AS y2
      ON y2.district_id = f.district_id
     AND y2.crop_year_start = f.crop_year_start - 2
    LEFT JOIN fact_kharif_rice_yield AS y3
      ON y3.district_id = f.district_id
     AND y3.crop_year_start = f.crop_year_start - 3
    WHERE f.crop_year_start BETWEEN 1998 AND 2005
)
SELECT COUNT(*),
       SUM(CASE WHEN yield_lag_1 IS NOT expected_lag THEN 1 ELSE 0 END),
       SUM(CASE WHEN (yield_avg_prior_3 IS NULL) <> (expected_avg IS NULL)
                  OR ABS(yield_avg_prior_3 - expected_avg) > 0.000001
                THEN 1 ELSE 0 END)
FROM expected;
