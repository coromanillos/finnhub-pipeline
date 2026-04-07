-- models/gold/government_dependency.sql
WITH lobbying_agg AS (
    SELECT
        ticker,
        SUM(expenses)           AS total_lobbying_expenses,
        SUM(income)             AS total_lobbying_income,
        COUNT(*)                AS lobbying_record_count
    FROM FINNHUB.FINNHUB_SILVER.lobbying
    GROUP BY ticker
),

spending_agg AS (
    SELECT
        ticker,
        SUM(obligated_amount)   AS total_obligated_amount,
        COUNT(*)                AS contract_count
    FROM FINNHUB.FINNHUB_SILVER.usa_spending
    GROUP BY ticker
),

profile AS (
    SELECT
        ticker,
        company_name,
        finnhub_industry,
        market_capitalization
    FROM FINNHUB.FINNHUB_SILVER.company_profile
)

SELECT
    p.ticker,
    p.company_name,
    p.finnhub_industry,
    p.market_capitalization,
    l.total_lobbying_expenses,
    l.total_lobbying_income,
    l.lobbying_record_count,
    s.total_obligated_amount,
    s.contract_count,
    -- derived metrics that make this model valuable
    ROUND(s.total_obligated_amount / NULLIF(p.market_capitalization, 0), 4)
                                    AS contracts_to_market_cap_ratio,
    ROUND(l.total_lobbying_expenses / NULLIF(s.total_obligated_amount, 0), 4)
                                    AS lobbying_per_contract_dollar
FROM profile p
LEFT JOIN lobbying_agg l    ON p.ticker = l.ticker
LEFT JOIN spending_agg s    ON p.ticker = s.ticker
ORDER BY s.total_obligated_amount DESC NULLS LAST