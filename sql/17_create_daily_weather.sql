CREATE TABLE IF NOT EXISTS fact_weather_daily (
    grid_lon REAL NOT NULL,
    grid_lat REAL NOT NULL,
    observation_date TEXT NOT NULL,
    temperature_c REAL,
    rainfall_mm REAL CHECK (rainfall_mm >= 0),
    PRIMARY KEY (grid_lon, grid_lat, observation_date)
);
