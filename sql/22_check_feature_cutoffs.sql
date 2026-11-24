SELECT COUNT(*) AS rows_checked,
       COUNT(CASE
           WHEN latest_weather_date IS NULL
             OR latest_weather_date > printf('%04d-07-31', crop_year_start)
           THEN 1 END) AS weather_violations,
       COUNT(CASE
           WHEN (yield_last_available IS NOT NULL AND last_yield_source_year IS NULL)
             OR last_yield_source_year > crop_year_start - 2
             OR (yield_trailing_avg_3 IS NOT NULL AND (
                 average_first_source_year IS NOT (crop_year_start - 4)
                 OR average_last_source_year IS NOT (crop_year_start - 2)
             ))
           THEN 1 END) AS yield_violations
FROM rice_forecast_features;
