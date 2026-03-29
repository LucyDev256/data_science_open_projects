-- Test: Check for duplicate patient UUIDs
-- Each patient_uuid should appear only once in the patients table

SELECT
    patient_uuid,
    COUNT(*) as occurrence_count
FROM {{ ref('silver_patients') }}
GROUP BY patient_uuid
HAVING COUNT(*) > 1
