-- Bronze Layer: Men's Health Orders
-- Source: Cloud SQL PostgreSQL (men_health database) via Debezium CDC
-- This model ingests raw order data including subscriptions and one-time purchases

{{ config(
    materialized='incremental',
    unique_key='order_id',
    tags=['bronze', 'operational', 'men']
) }}

WITH source_data AS (
    SELECT
        order_id,
        patient_uuid,
        order_date,
        status,
        order_type,
        total_amount,
        payment_status,
        payment_method,
        fulfillment_partner,
        shipping_address_id,
        tracking_number,
        created_at,
        updated_at,
        -- CDC metadata
        _kafka_timestamp AS ingestion_timestamp,
        _kafka_partition,
        _kafka_offset
    FROM {{ source('debezium_men', 'orders') }}
    
    {% if is_incremental() %}
    WHERE _kafka_timestamp > (SELECT MAX(ingestion_timestamp) FROM {{ this }})
    {% endif %}
)

SELECT
    *,
    CURRENT_TIMESTAMP() AS processed_at
FROM source_data
