SELECT district_id, crop_year_start, yield_kg_per_ha
FROM fact_kharif_rice_yield
WHERE crop_year_start <= :forecast_year - :delay_years
  AND yield_kg_per_ha IS NOT NULL
ORDER BY crop_year_start, district_id;
