WITH base AS (
    SELECT unique_key, created_date, closed_date, agency, complaint_type, borough,
           CASE WHEN closed_date IS NULL THEN NULL
                ELSE date_diff('hour', created_date, closed_date) END AS resolution_hours
    FROM read_parquet('data/curated/nyc311.parquet')
)
SELECT agency, borough, COUNT(*) AS requests,
       AVG(CASE WHEN closed_date IS NOT NULL THEN 1.0 ELSE 0.0 END) * 100 AS closed_rate_pct,
       MEDIAN(resolution_hours) AS median_resolution_hours,
       QUANTILE_CONT(resolution_hours, 0.90) AS p90_resolution_hours
FROM base
GROUP BY 1, 2
ORDER BY requests DESC;
