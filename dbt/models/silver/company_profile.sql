-- models/silver/company_profile.sql
-- GOOD
SELECT
    ticker,
    pulled_at,
    data:country::VARCHAR                 AS country,
    data:currency::VARCHAR                AS currency,
    data:estimateCurrency::VARCHAR        AS estimate_currency,
    data:exchange::VARCHAR                AS exchange,
    data:finnhubIndustry::VARCHAR         AS finnhub_industry,
    data:ipo::VARCHAR                     AS ipo,
    data:logo::VARCHAR                    AS logo,
    data:marketCapitalization::FLOAT      AS market_capitalization,
    data:"name"::VARCHAR                  AS company_name,
    data:phone::VARCHAR                   AS phone,
    data:shareOutstanding::FLOAT          AS share_outstanding,
    --data:ticker::VARCHAR                  AS finnhub_ticker,
    data:weburl::VARCHAR                  AS weburl
FROM FINNHUB.FINNHUB_BRONZE.company_profile_raw