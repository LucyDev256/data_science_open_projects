-- Test: Check for orphaned prescriptions
-- All prescriptions should have a valid provider_id and patient_uuid

WITH prescriptions AS (
    SELECT DISTINCT provider_id, patient_uuid
    FROM {{ ref('silver_prescriptions') }}
    WHERE provider_id IS NOT NULL
      AND patient_uuid IS NOT NULL
),

providers AS (
    SELECT DISTINCT provider_id
    FROM {{ ref('silver_providers') }}
),

patients AS (
    SELECT DISTINCT patient_uuid
    FROM {{ ref('silver_patients') }}
)

SELECT
    p.provider_id,
    p.patient_uuid,
    CASE 
        WHEN pr.provider_id IS NULL THEN 'Missing provider'
        WHEN pt.patient_uuid IS NULL THEN 'Missing patient'
    END as issue
FROM prescriptions p
LEFT JOIN providers pr ON p.provider_id = pr.provider_id
LEFT JOIN patients pt ON p.patient_uuid = pt.patient_uuid
WHERE pr.provider_id IS NULL 
   OR pt.patient_uuid IS NULL
