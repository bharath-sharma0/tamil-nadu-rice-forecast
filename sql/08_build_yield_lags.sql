DROP VIEW IF EXISTS rice_yield_history_features;

CREATE VIEW rice_yield_history_features AS
SELECT
    district_id,
    crop_year_start,
    yield_kg_per_ha,
    LAG(yield_kg_per_ha, 1) OVER (
        PARTITION BY district_id ORDER BY crop_year_start
    ) AS yield_lag_1,
    CASE WHEN COUNT(yield_kg_per_ha) OVER prior_three = 3
         THEN AVG(yield_kg_per_ha) OVER prior_three
    END AS yield_avg_prior_3
FROM fact_kharif_rice_yield
WINDOW prior_three AS (
    PARTITION BY district_id ORDER BY crop_year_start
    ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
);
