-- models/silver/eps_surprises.sql
-- GOOD
SELECT
    ticker,
    pulled_at,
    entry.value:actual::FLOAT           AS actual,
    entry.value:estimate::FLOAT         AS estimate,
    entry.value:period::VARCHAR         AS period,
    entry.value:quarter::INT            AS quarter,
    entry.value:surprise::FLOAT         AS surprise,
    entry.value:surprisePercent::FLOAT  AS surprise_percent,
    entry.value:symbol::VARCHAR         AS symbol,
    entry.value:year::INT               AS year
FROM FINNHUB.FINNHUB_BRONZE.eps_surprises_raw,
    LATERAL FLATTEN(input => data:data) AS entry