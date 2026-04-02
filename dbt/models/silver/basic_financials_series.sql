-- models/silver/basic_financials_series.sql
-- Exploded time-series entries from the series block
-- One row per ticker per series_name per period
-- Covers both annual and quarterly granularities
SELECT
    ticker,
    pulled_at,
    'annual'                                                        AS frequency,
    series_entry.key::VARCHAR                                       AS series_name,
    data_point.value:period::VARCHAR                                AS period,
    data_point.value:v::FLOAT                                       AS value
FROM FINNHUB.FINNHUB_BRONZE.basic_financials_raw,
    LATERAL FLATTEN(input => data:series:annual)                    AS series_entry,
    LATERAL FLATTEN(input => series_entry.value)                    AS data_point

UNION ALL

SELECT
    ticker,
    pulled_at,
    'quarterly'                                                     AS frequency,
    series_entry.key::VARCHAR                                       AS series_name,
    data_point.value:period::VARCHAR                                AS period,
    data_point.value:v::FLOAT                                       AS value
FROM FINNHUB.FINNHUB_BRONZE.basic_financials_raw,
    LATERAL FLATTEN(input => data:series:quarterly)                 AS series_entry,
    LATERAL FLATTEN(input => series_entry.value)                    AS data_point