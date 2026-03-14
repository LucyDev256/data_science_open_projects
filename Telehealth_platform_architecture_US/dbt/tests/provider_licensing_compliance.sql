-- Test: Verify provider multi-state licensing
-- Providers serving multiple states must have valid licenses in those states

WITH provider_consultations AS (
    SELECT DISTINCT
        provider_id,
        patient_state
    FROM {{ ref('silver_consultations') }}
),

provider_licenses AS (
    SELECT DISTINCT
        provider_id,
        state
    FROM {{ ref('silver_provider_licenses') }}
    WHERE status = 'ACTIVE'
      AND expiration_date > CURRENT_DATE
)

SELECT
    pc.provider_id,
    pc.patient_state,
    'Unlicensed in patient state' as issue
FROM provider_consultations pc
LEFT JOIN provider_licenses pl 
    ON pc.provider_id = pl.provider_id 
    AND pc.patient_state = pl.state
WHERE pl.state IS NULL
