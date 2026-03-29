-- Bronze Layer: Shared Providers Data
-- Source: Cloud SQL PostgreSQL (shared database) via Debezium CDC
-- This model ingests provider/practitioner data shared across both brands

{{ config(
    materialized='incremental',
    unique_key='provider_id',
    tags=['bronze', 'shared', 'clinical']
) }}

WITH source_data AS (
    SELECT
        provider_id,
        first_name,
        last_name,
        npi_number,
        dea_number,
        specialty,
        email,
        phone,
        license_states,
        telemedicine_certified,
        is_active,
        hire_date,
        created_at,
        updated_at,
        -- CDC metadata
        _kafka_timestamp AS ingestion_timestamp,
        _kafka_partition,
        _kafka_offset
    FROM {{ source('debezium_shared', 'providers') }}
    
    {% if is_incremental() %}
    WHERE _kafka_timestamp > (SELECT MAX(ingestion_timestamp) FROM {{ this }})
    {% endif %}
)

SELECT
    *,
    CURRENT_TIMESTAMP() AS processed_at
FROM source_data
