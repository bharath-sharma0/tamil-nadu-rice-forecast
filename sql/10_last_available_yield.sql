DROP VIEW IF EXISTS rice_yield_last_available;

CREATE VIEW rice_yield_last_available AS
WITH eligible_history AS (
    SELECT
        target.district_id,
        target.crop_year_start,
        (
            SELECT MAX(history.crop_year_start)
            FROM fact_kharif_rice_yield AS history
            WHERE history.district_id = target.district_id
              AND history.crop_year_start <= target.crop_year_start - 2
              AND history.yield_kg_per_ha IS NOT NULL
        ) AS source_year
    FROM fact_kharif_rice_yield AS target
)
SELECT e.district_id, e.crop_year_start, e.source_year,
       h.yield_kg_per_ha AS baseline_last_available
FROM eligible_history AS e
LEFT JOIN fact_kharif_rice_yield AS h
  ON h.district_id = e.district_id
 AND h.crop_year_start = e.source_year;
