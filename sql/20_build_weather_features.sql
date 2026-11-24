DROP VIEW IF EXISTS district_weather_features;

CREATE VIEW district_weather_features AS
SELECT
    district_id,
    crop_year_start,
    MAX(latest_observation_date) AS latest_weather_date,
    COUNT(*) AS months_available,
    MAX(CASE WHEN month = 1 THEN rainfall_mm END) AS rainfall_mm_01,
    MAX(CASE WHEN month = 1 THEN mean_temperature_c END) AS temperature_c_01,
    MAX(CASE WHEN month = 2 THEN rainfall_mm END) AS rainfall_mm_02,
    MAX(CASE WHEN month = 2 THEN mean_temperature_c END) AS temperature_c_02,
    MAX(CASE WHEN month = 3 THEN rainfall_mm END) AS rainfall_mm_03,
    MAX(CASE WHEN month = 3 THEN mean_temperature_c END) AS temperature_c_03,
    MAX(CASE WHEN month = 4 THEN rainfall_mm END) AS rainfall_mm_04,
    MAX(CASE WHEN month = 4 THEN mean_temperature_c END) AS temperature_c_04,
    MAX(CASE WHEN month = 5 THEN rainfall_mm END) AS rainfall_mm_05,
    MAX(CASE WHEN month = 5 THEN mean_temperature_c END) AS temperature_c_05,
    MAX(CASE WHEN month = 6 THEN rainfall_mm END) AS rainfall_mm_06,
    MAX(CASE WHEN month = 6 THEN mean_temperature_c END) AS temperature_c_06,
    MAX(CASE WHEN month = 7 THEN rainfall_mm END) AS rainfall_mm_07,
    MAX(CASE WHEN month = 7 THEN mean_temperature_c END) AS temperature_c_07
FROM district_weather_monthly
GROUP BY district_id, crop_year_start;
