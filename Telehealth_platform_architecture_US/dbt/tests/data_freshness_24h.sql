-- Test: Validate data freshness
-- Bronze layer tables should be updated within the last 24 hours

SELECT
    '{{ this }}' as table_name,
    MAX(processed_at) as last_update,
    TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(processed_at), HOUR) as hours_since_update
FROM {{ this }}
HAVING TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(processed_at), HOUR) > 24
