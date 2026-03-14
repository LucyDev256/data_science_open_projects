-- Test: Ensure no PHI in analytics tables
-- All analytics tables should use patient_uuid_hash, not raw patient_uuid

SELECT
    patient_uuid
FROM {{ ref('gold_patient_journey') }}
WHERE patient_uuid IS NOT NULL
  AND patient_uuid NOT LIKE 'hash_%'
LIMIT 1
