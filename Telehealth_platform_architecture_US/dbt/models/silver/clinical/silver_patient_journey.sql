-- Silver Layer: De-identified Patient Journey
-- Combines consultation and prescription data without PHI

{{ config(
    materialized='table',
    tags=['silver', 'clinical', 'deidentified']
) }}

WITH men_patients AS (
    SELECT
        id AS patient_uuid,
        'mens' AS brand,
        registration_date,
        is_active
    FROM {{ ref('bronze_men_patients') }}
),

women_patients AS (
    SELECT
        id AS patient_uuid,
        'womens' AS brand,
        registration_date,
        is_active
    FROM {{ ref('bronze_women_patients') }}
),

all_patients AS (
    SELECT * FROM men_patients
    UNION ALL
    SELECT * FROM women_patients
),

consultations AS (
    SELECT
        c.id AS consultation_id,
        c.patient_id AS patient_uuid,
        c.provider_id,
        c.consultation_type,
        c.status,
        c.scheduled_at,
        c.started_at,
        c.completed_at,
        c.chief_complaint,
        c.product_interest,
        c.created_at
    FROM {{ ref('bronze_men_consultations') }} c
    UNION ALL
    SELECT
        c.id AS consultation_id,
        c.patient_id AS patient_uuid,
        c.provider_id,
        c.consultation_type,
        c.status,
        c.scheduled_at,
        c.started_at,
        c.completed_at,
        c.chief_complaint,
        c.product_interest,
        c.created_at
    FROM {{ ref('bronze_women_consultations') }} c
),

prescriptions AS (
    SELECT
        p.id AS prescription_id,
        p.patient_id AS patient_uuid,
        p.consultation_id,
        p.provider_id,
        p.product_id,
        p.status,
        p.approved_at,
        p.auto_refill_enabled,
        p.next_refill_date,
        p.created_at
    FROM {{ ref('bronze_men_prescriptions') }} p
    UNION ALL
    SELECT
        p.id AS prescription_id,
        p.patient_id AS patient_uuid,
        p.consultation_id,
        p.provider_id,
        p.product_id,
        p.status,
        p.approved_at,
        p.auto_refill_enabled,
        p.next_refill_date,
        p.created_at
    FROM {{ ref('bronze_women_prescriptions') }} p
)

SELECT
    p.patient_uuid,
    
    -- Apply de-identification hash (one-way hash for analytics)
    {{ deidentify_patient_uuid('p.patient_uuid') }} AS patient_token_hash,
    
    p.brand,
    p.registration_date,
    p.is_active,
    
    -- Consultation metrics
    COUNT(DISTINCT c.consultation_id) AS total_consultations,
    COUNT(DISTINCT CASE WHEN c.status = 'COMPLETED' THEN c.consultation_id END) AS completed_consultations,
    MIN(c.created_at) AS first_consultation_date,
    MAX(c.created_at) AS most_recent_consultation_date,
    
    -- Prescription metrics
    COUNT(DISTINCT pr.prescription_id) AS total_prescriptions,
    COUNT(DISTINCT CASE WHEN pr.status = 'APPROVED' THEN pr.prescription_id END) AS approved_prescriptions,
    COUNT(DISTINCT pr.product_id) AS unique_products_prescribed,
    
    -- Engagement indicators
    CASE 
        WHEN COUNT(pr.prescription_id) > 0 AND pr.auto_refill_enabled = TRUE THEN 'auto_refill'
        WHEN COUNT(pr.prescription_id) > 2 THEN 'repeat_customer'
        WHEN COUNT(pr.prescription_id) = 1 THEN 'single_purchase'
        ELSE 'no_purchase'
    END AS patient_segment,
    
    CURRENT_TIMESTAMP() AS processed_at
    
FROM all_patients p
LEFT JOIN consultations c ON p.patient_uuid = c.patient_uuid
LEFT JOIN prescriptions pr ON p.patient_uuid = pr.patient_uuid

GROUP BY 
    p.patient_uuid,
    p.brand,
    p.registration_date,
    p.is_active,
    pr.auto_refill_enabled
