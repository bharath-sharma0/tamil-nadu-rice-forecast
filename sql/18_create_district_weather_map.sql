CREATE TABLE IF NOT EXISTS district_weather_map (
    district_id INTEGER PRIMARY KEY REFERENCES dim_district(district_id),
    point_lon REAL NOT NULL,
    point_lat REAL NOT NULL,
    grid_lon REAL NOT NULL,
    grid_lat REAL NOT NULL
);
