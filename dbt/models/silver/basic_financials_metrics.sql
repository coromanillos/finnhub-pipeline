-- models/silver/basic_financials_metrics.sql
-- Flat scalar metrics from the metric block
-- One row per ticker per pull date
SELECT
    ticker,
    pulled_at,
    data:metric:"10DayAverageTradingVolume"::FLOAT        AS ten_day_avg_trading_volume,
    data:metric:"13WeekPriceReturnDaily"::FLOAT           AS thirteen_week_price_return_daily,
    data:metric:"26WeekPriceReturnDaily"::FLOAT           AS twenty_six_week_price_return_daily,
    data:metric:"52WeekHigh"::FLOAT                       AS fifty_two_week_high,
    data:metric:"52WeekHighDate"::VARCHAR                 AS fifty_two_week_high_date,
    data:metric:"52WeekLow"::FLOAT                        AS fifty_two_week_low,
    data:metric:"52WeekLowDate"::VARCHAR                  AS fifty_two_week_low_date,
    data:metric:"52WeekPriceReturnDaily"::FLOAT           AS fifty_two_week_price_return_daily,
    data:metric:"5DayPriceReturnDaily"::FLOAT             AS five_day_price_return_daily, -- Was missing
    data:metric:assetTurnoverAnnual::FLOAT              AS asset_turnover_annual,
    data:metric:assetTurnoverTTM::FLOAT                 AS asset_turnover_ttm,
    data:metric:beta::FLOAT                             AS beta,
    data:metric:bookValuePerShareAnnual::FLOAT          AS book_value_per_share_annual, -- Was missing
    data:metric:bookValuePerShareQuarterly::FLOAT AS book_value_per_share_quarterly, -- Was missing
    data:metric:bookValueShareGrowth5Y::FLOAT           AS book_value_share_growth_five_year, -- Was missing
    data:metric:marketCapitalization::FLOAT             AS market_capitalization,
    data:metric:enterpriseValue::FLOAT                  AS enterprise_value,
    data:metric:forwardPE::FLOAT                        AS forward_pe,
    data:metric:peAnnual::FLOAT                         AS pe_annual,
    data:metric:peTTM::FLOAT                            AS pe_ttm,
    data:metric:pbAnnual::FLOAT                         AS pb_annual,
    data:metric:psAnnual::FLOAT                         AS ps_annual,
    data:metric:psTTM::FLOAT                            AS ps_ttm,
    data:metric:epsAnnual::FLOAT                        AS eps_annual,
    data:metric:epsTTM::FLOAT                           AS eps_ttm,
    data:metric:epsGrowth3Y::FLOAT                      AS eps_growth_3y,
    data:metric:epsGrowth5Y::FLOAT                      AS eps_growth_5y,
    data:metric:grossMarginAnnual::FLOAT                AS gross_margin_annual,
    data:metric:grossMarginTTM::FLOAT                   AS gross_margin_ttm,
    data:metric:grossMargin5Y::FLOAT                    AS gross_margin_5y,
    data:metric:netProfitMarginAnnual::FLOAT            AS net_profit_margin_annual,
    data:metric:netProfitMarginTTM::FLOAT               AS net_profit_margin_ttm,
    data:metric:netProfitMargin5Y::FLOAT                AS net_profit_margin_5y,
    data:metric:operatingMarginAnnual::FLOAT            AS operating_margin_annual,
    data:metric:operatingMarginTTM::FLOAT               AS operating_margin_ttm,
    data:metric:operatingMargin5Y::FLOAT                AS operating_margin_5y,
    data:metric:roaAnnual::FLOAT                        AS roa_annual, -- GOOD
    data:metric:roaRfy::FLOAT                           AS roa_rfy,
    data:metric:roaTTM::FLOAT                           AS roa_ttm,
    data:metric:roa5Y::FLOAT                            AS roa_5y,
    data:metric:roeTTM::FLOAT                           AS roe_ttm,
    data:metric:roeRfy::FLOAT                           AS roe_rfy,
    data:metric:roe5Y::FLOAT                            AS roe_5y,
    data:metric:roiAnnual::FLOAT                        AS roi_annual,
    data:metric:roiTTM::FLOAT                           AS roi_ttm,
    data:metric:roi5Y::FLOAT                            AS roi_5y,
    data:metric:revenueGrowth3Y::FLOAT                  AS revenue_growth_3y,
    data:metric:revenueGrowth5Y::FLOAT                  AS revenue_growth_5y,
    data:metric:revenueGrowthTTMYoy::FLOAT              AS revenue_growth_ttm_yoy,
    data:metric:currentRatioAnnual::FLOAT               AS current_ratio_annual,
    data:metric:currentRatioQuarterly::FLOAT            AS current_ratio_quarterly,
    data:metric:quickRatioAnnual::FLOAT                 AS quick_ratio_annual,
    data:metric:quickRatioQuarterly::FLOAT              AS quick_ratio_quarterly,
    data:metric:dividendYieldIndicatedAnnual::FLOAT     AS dividend_yield_indicated_annual,
    data:metric:dividendPerShareAnnual::FLOAT           AS dividend_per_share_annual,
    data:metric:dividendGrowthRate5Y::FLOAT             AS dividend_growth_rate_5y,
    data:metric:payoutRatioAnnual::FLOAT                AS payout_ratio_annual,
    data:metric:payoutRatioTTM::FLOAT                   AS payout_ratio_ttm,
    data:metric:"longTermDebt/equityAnnual"::FLOAT        AS long_term_debt_equity_annual, --error
    data:metric:"longTermDebt/equityQuarterly"::FLOAT        AS long_term_debt_equity_quarterly, --error
    data:metric:"totalDebt/totalEquityAnnual"::FLOAT      AS total_debt_equity_annual,  --error
    data:metric:"totalDebt/totalEquityQuarterly"::FLOAT      AS total_debt_equity_quarterly,  --error
    data:metric:inventoryTurnoverAnnual::FLOAT          AS inventory_turnover_annual,
    data:metric:inventoryTurnoverTTM::FLOAT             AS inventory_turnover_ttm,
    data:metric:receivablesTurnoverAnnual::FLOAT        AS receivables_turnover_annual,
    data:metric:receivablesTurnoverTTM::FLOAT           AS receivables_turnover_ttm
FROM FINNHUB.FINNHUB_BRONZE.basic_financials_raw