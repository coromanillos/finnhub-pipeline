-- models/silver/eps_surprises.sql

SELECT
    ticker,
    pulled_at,
    data:actual::FLOAT          AS actual,
    data:estimate::FLOAT        AS estimate,
    data:period::VARCHAR        AS period,
    data:quarter::VARCHAR       AS quarter,
    data:surprise::FLOAT        AS surprise,
    data:surprisePercent::FLOAT AS surprise_percent,
    data:symbol::VARCHAR        AS symbol,
    data:year::VARCHAR          AS year
FROM FINNHUB.FINNHUB_BRONZE.eps_surprises_raw,
LATERAL FLATTEN(input => data:data)  -- Unnest the array