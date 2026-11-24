SELECT y.crop_year_start, y.yield_kg_per_ha
FROM fact_kharif_rice_yield AS y
JOIN dim_district AS d USING (district_id)
WHERE d.district_name = :district
  AND y.crop_year_start BETWEEN :forecast_year - 4 AND :forecast_year - 2
ORDER BY y.crop_year_start;
