-- Bronze Layer: Men's Health Products
-- Source: Cloud SQL PostgreSQL (men_health database) via Debezium CDC
-- This model ingests raw product data from the men's health operational database

{{ config(
    materialized='table',
    tags=['bronze', 'pharmaceutical', 'men']
) }}

WITH source_data AS (
    SELECT
        id,
        sku,
        name,
        category,
        description,
        active_ingredients,
        dosage_form,
        strength,
        requires_dea,
        fda_approved,
        ndc_code,
        base_price,
        subscription_price,
        insurance_coverable,
        is_active,
        created_at,
        updated_at,
        -- CDC metadata
        _kafka_timestamp AS ingestion_timestamp,
        _kafka_partition,
        _kafka_offset
    FROM {{ source('debezium_men', 'products') }}
)

SELECT
    *,
    CURRENT_TIMESTAMP() AS processed_at
FROM source_data
