-- Bronze Layer: Men's Health Consultations
-- Source: Cloud SQL PostgreSQL (men_health database) via Debezium CDC
-- This model ingests raw consultation data (async and video consultations)

{{ config(
    materialized='incremental',
    unique_key='consultation_id',
    tags=['bronze', 'clinical', 'men']
) }}

WITH source_data AS (
    SELECT
        consultation_id,
        patient_uuid,
        provider_id,
        consultation_type,
        consultation_date,
        status,
        chief_complaint,
        assessment_notes,
        treatment_plan,
        duration_minutes,
        created_at,
        updated_at,
        -- CDC metadata
        _kafka_timestamp AS ingestion_timestamp,
        _kafka_partition,
        _kafka_offset
    FROM {{ source('debezium_men', 'consultations') }}
    
    {% if is_incremental() %}
    WHERE _kafka_timestamp > (SELECT MAX(ingestion_timestamp) FROM {{ this }})
    {% endif %}
)

SELECT
    *,
    CURRENT_TIMESTAMP() AS processed_at
FROM source_data
