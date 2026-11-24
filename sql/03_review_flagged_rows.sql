SELECT district_name, crop_year_start, area_ha, production_tonnes,
       reported_yield_tonnes_per_ha
FROM rice_yield_staging
WHERE (area_ha IS NOT NULL
       OR production_tonnes IS NOT NULL
       OR reported_yield_tonnes_per_ha IS NOT NULL)
  AND (area_ha IS NULL OR area_ha <= 0
       OR production_tonnes IS NULL OR production_tonnes <= 0
       OR reported_yield_tonnes_per_ha IS NULL
       OR reported_yield_tonnes_per_ha <= 0)
ORDER BY district_name, crop_year_start;
