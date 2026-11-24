DROP VIEW IF EXISTS rice_forecast_features;

CREATE VIEW rice_forecast_features AS
SELECT
    y.district_id,
    y.crop_year_start,
    y.yield_kg_per_ha AS target_yield_kg_per_ha,
    l.baseline_last_available AS yield_last_available,
    l.source_year AS last_yield_source_year,
    a.baseline_avg_3 AS yield_trailing_avg_3,
    a.first_source_year AS average_first_source_year,
    a.last_source_year AS average_last_source_year,
    w.latest_weather_date,
    w.rainfall_mm_01,
    w.temperature_c_01,
    w.rainfall_mm_02,
    w.temperature_c_02,
    w.rainfall_mm_03,
    w.temperature_c_03,
    w.rainfall_mm_04,
    w.temperature_c_04,
    w.rainfall_mm_05,
    w.temperature_c_05,
    w.rainfall_mm_06,
    w.temperature_c_06,
    w.rainfall_mm_07,
    w.temperature_c_07
FROM fact_kharif_rice_yield AS y
LEFT JOIN rice_yield_last_available AS l USING (district_id, crop_year_start)
LEFT JOIN rice_yield_trailing_average AS a USING (district_id, crop_year_start)
LEFT JOIN district_weather_features AS w USING (district_id, crop_year_start);
