-- models/gold/ticker_scorecard.sql
WITH company AS (
    SELECT
        ticker,
        company_name,
        finnhub_industry,
        exchange,
        country,
        market_capitalization,
        ipo
    FROM FINNHUB.FINNHUB_SILVER.company_profile
),

metrics AS (
    SELECT
        ticker,
        beta,
        market_capitalization       AS metrics_market_cap,
        pe_annual,
        pe_ttm,
        eps_annual,
        eps_ttm,
        eps_growth_3y,
        eps_growth_5y,
        gross_margin_annual,
        gross_margin_ttm,
        net_profit_margin_annual,
        net_profit_margin_ttm,
        operating_margin_annual,
        operating_margin_ttm,
        roe_ttm,
        roa_ttm,
        revenue_growth_3y,
        revenue_growth_5y,
        dividend_yield_indicated_annual,
        long_term_debt_equity_annual,
        current_ratio_annual,
        enterprise_value,
        forward_pe
    FROM FINNHUB.FINNHUB_SILVER.basic_financials_metrics
),

latest_eps AS (
    SELECT
        ticker,
        actual,
        estimate,
        surprise,
        surprise_percent,
        period,
        quarter,
        year
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY ticker
                ORDER BY period DESC
            ) AS rn
        FROM FINNHUB.FINNHUB_SILVER.eps_surprises
    )
    WHERE rn = 1
),

lobbying_agg AS (
    SELECT
        ticker,
        COUNT(*)        AS lobbying_record_count,
        SUM(income)     AS total_lobbying_income,
        SUM(expenses)   AS total_lobbying_expenses
    FROM FINNHUB.FINNHUB_SILVER.lobbying
    GROUP BY ticker
),

spending_agg AS (
    SELECT
        ticker,
        COUNT(*)                    AS spending_record_count,
        SUM(obligated_amount)       AS total_obligated_amount,
        SUM(outlayed_amount)        AS total_outlayed_amount
    FROM FINNHUB.FINNHUB_SILVER.usa_spending
    GROUP BY ticker
)

SELECT
    -- company identity
    c.ticker,
    c.company_name,
    c.finnhub_industry,
    c.exchange,
    c.country,
    c.market_capitalization,
    c.ipo,

    -- valuation
    m.pe_annual,
    m.pe_ttm,
    m.forward_pe,
    m.enterprise_value,
    m.beta,

    -- profitability
    m.eps_annual,
    m.eps_ttm,
    m.eps_growth_3y,
    m.eps_growth_5y,
    m.gross_margin_annual,
    m.gross_margin_ttm,
    m.net_profit_margin_annual,
    m.net_profit_margin_ttm,
    m.operating_margin_annual,
    m.operating_margin_ttm,
    m.roe_ttm,
    m.roa_ttm,
    m.revenue_growth_3y,
    m.revenue_growth_5y,

    -- dividends and leverage
    m.dividend_yield_indicated_annual,
    m.long_term_debt_equity_annual,
    m.current_ratio_annual,

    -- latest eps surprise
    e.actual                AS latest_eps_actual,
    e.estimate              AS latest_eps_estimate,
    e.surprise              AS latest_eps_surprise,
    e.surprise_percent      AS latest_eps_surprise_pct,
    e.period                AS latest_eps_period,
    e.quarter               AS latest_eps_quarter,
    e.year                  AS latest_eps_year,

    -- lobbying
    l.lobbying_record_count,
    l.total_lobbying_income,
    l.total_lobbying_expenses,

    -- government spending
    s.spending_record_count,
    s.total_obligated_amount,
    s.total_outlayed_amount

FROM company c
LEFT JOIN metrics m          ON c.ticker = m.ticker
LEFT JOIN latest_eps e       ON c.ticker = e.ticker
LEFT JOIN lobbying_agg l     ON c.ticker = l.ticker
LEFT JOIN spending_agg s     ON c.ticker = s.ticker