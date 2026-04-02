-- models/silver/lobbying.sql

SELECT
    ticker,
    pulled_at,
    value:clientId::VARCHAR           AS client_id,
    value:country::VARCHAR            AS country,
    value:date::VARCHAR               AS filing_date,
    value:description::VARCHAR        AS description,
    value:documentUrl::VARCHAR        AS document_url,
    value:expenses::FLOAT             AS expenses,
    value:houseRegistrantId::VARCHAR  AS house_registrant_id,
    value:income::INTEGER             AS income,
    value:name::VARCHAR               AS company_name,
    value:period::VARCHAR             AS period,
    value:postedName::VARCHAR         AS posted_name,
    value:registrantId::VARCHAR       AS registrant_id,
    value:senateId::VARCHAR           AS senate_id,
    data:symbol::VARCHAR              AS symbol,
    value:year::VARCHAR               AS year
FROM FINNHUB.FINNHUB_BRONZE.lobbying_raw,
LATERAL FLATTEN(input => data:data)