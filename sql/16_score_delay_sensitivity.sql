WITH observed AS (
    SELECT district_id, crop_year_start, yield_kg_per_ha AS actual
    FROM fact_kharif_rice_yield
    WHERE crop_year_start BETWEEN :first_year AND :last_year
      AND yield_kg_per_ha IS NOT NULL
),
history AS (
    SELECT
        o.district_id, o.crop_year_start, o.actual,
        MAX(h.crop_year_start) AS last_source_year,
        COUNT(CASE WHEN h.crop_year_start >= o.crop_year_start - :delay - 2
                   THEN 1 END) AS seasons,
        AVG(CASE WHEN h.crop_year_start >= o.crop_year_start - :delay - 2
                 THEN h.yield_kg_per_ha END) AS average_yield
    FROM observed AS o
    LEFT JOIN fact_kharif_rice_yield AS h
      ON h.district_id = o.district_id
     AND h.crop_year_start <= o.crop_year_start - :delay
     AND h.yield_kg_per_ha IS NOT NULL
    GROUP BY o.district_id, o.crop_year_start, o.actual
)
SELECT h.district_id, h.crop_year_start, h.actual, h.last_source_year,
       y.yield_kg_per_ha AS last_forecast,
       CASE WHEN h.seasons = 3 THEN h.average_yield END AS average_forecast
FROM history AS h
LEFT JOIN fact_kharif_rice_yield AS y
  ON y.district_id = h.district_id
 AND y.crop_year_start = h.last_source_year;
