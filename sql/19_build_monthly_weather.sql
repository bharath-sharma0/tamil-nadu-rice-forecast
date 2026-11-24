DROP VIEW IF EXISTS district_weather_monthly;

CREATE VIEW district_weather_monthly AS
WITH monthly AS (
    SELECT
        grid_lon, grid_lat,
        CAST(substr(observation_date, 1, 4) AS INTEGER) AS crop_year_start,
        CAST(substr(observation_date, 6, 2) AS INTEGER) AS month,
        MAX(observation_date) AS latest_observation_date,
        COUNT(rainfall_mm) AS rainfall_days,
        COUNT(temperature_c) AS temperature_days,
        SUM(rainfall_mm) AS total_rainfall,
        AVG(temperature_c) AS mean_temperature
    FROM fact_weather_daily
    WHERE substr(observation_date, 6, 2) BETWEEN '01' AND '07'
    GROUP BY grid_lon, grid_lat, crop_year_start, month
),
coverage AS (
    SELECT *,
           date(printf('%04d-%02d-01', crop_year_start, month),
                '+1 month', '-1 day') AS month_end
    FROM monthly
)
SELECT
    m.district_id, c.crop_year_start, c.month, c.latest_observation_date,
    CASE WHEN c.rainfall_days = CAST(substr(c.month_end, 9, 2) AS INTEGER)
         THEN c.total_rainfall END AS rainfall_mm,
    CASE WHEN c.temperature_days = CAST(substr(c.month_end, 9, 2) AS INTEGER)
         THEN c.mean_temperature END AS mean_temperature_c
FROM coverage AS c
JOIN district_weather_map AS m
  ON m.grid_lon = c.grid_lon AND m.grid_lat = c.grid_lat;
