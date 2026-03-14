-- Bronze Layer: Women's Health Prescriptions
-- Source: Cloud SQL PostgreSQL (women_health database) via Debezium CDC
-- This model ingests raw prescription data with DEA tracking for controlled substances

{{ config(
    materialized='incremental',
    unique_key='prescription_id',
    tags=['bronze', 'clinical', 'pharmaceutical', 'women']
) }}

WITH source_data AS (
    SELECT
        prescription_id,
        patient_uuid,
        provider_id,
        consultation_id,
        product_id,
        medication_name,
        dosage_instructions,
        quantity,
        refills_allowed,
        refills_remaining,
        prescribed_date,
        expiration_date,
        status,
        is_controlled_substance,
        dea_schedule,
        pharmacy_id,
        created_at,
        updated_at,
        -- CDC metadata
        _kafka_timestamp AS ingestion_timestamp,
        _kafka_partition,
        _kafka_offset
    FROM {{ source('debezium_women', 'prescriptions') }}
    
    {% if is_incremental() %}
    WHERE _kafka_timestamp > (SELECT MAX(ingestion_timestamp) FROM {{ this }})
    {% endif %}
)

SELECT
    *,
    CURRENT_TIMESTAMP() AS processed_at
FROM source_data
