SELECT DISTINCT
    crop_year_start,
    CASE
        WHEN crop_year_start <= 2011 THEN 'initial history'
        WHEN crop_year_start <= 2017 THEN 'development'
        WHEN crop_year_start <= 2019 THEN 'buffer'
        ELSE 'final test'
    END AS evaluation_role
FROM fact_kharif_rice_yield
ORDER BY crop_year_start;
