-- Optional checks after importing analytical_distributor_month.csv into SQL.

-- Check duplicate distributor-month keys.
SELECT cnpj, year_month, COUNT(*) AS rows_per_key
FROM analytical_distributor_month
GROUP BY cnpj, year_month
HAVING COUNT(*) > 1;

-- Check DEC/FEC proxy coverage.
SELECT
    COUNT(*) AS total_rows,
    SUM(CASE WHEN DEC_unweighted_mean_proxy IS NULL THEN 1 ELSE 0 END) AS missing_dec,
    SUM(CASE WHEN FEC_unweighted_mean_proxy IS NULL THEN 1 ELSE 0 END) AS missing_fec
FROM analytical_distributor_month;

-- Check monthly distributor coverage.
SELECT year_month, COUNT(DISTINCT cnpj) AS distributors
FROM analytical_distributor_month
GROUP BY year_month
ORDER BY year_month;
