-- Bronze Layer: Inventory
-- Real-time inventory data for both brands

{{ config(
    materialized='incremental',
    unique_key='id',
    tags=['bronze', 'inventory', 'realtime']
) }}

-- Men's Health Inventory
WITH men_inventory AS (
    SELECT
        'mens' AS brand,
        id,
        product_id,
        fulfillment_partner,
        lot_number,
        expiration_date,
        quantity_available,
        quantity_reserved,
        quantity_on_hold,
        warehouse_location,
        bin_location,
        received_date,
        last_audit_date,
        created_at,
        updated_at,
        _kafka_timestamp AS ingestion_timestamp
    FROM {{ source('debezium_men', 'inventory') }}
    {% if is_incremental() %}
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
),

-- Women's Health Inventory
women_inventory AS (
    SELECT
        'womens' AS brand,
        id,
        product_id,
        fulfillment_partner,
        lot_number,
        expiration_date,
        quantity_available,
        quantity_reserved,
        quantity_on_hold,
        warehouse_location,
        bin_location,
        received_date,
        last_audit_date,
        created_at,
        updated_at,
        _kafka_timestamp AS ingestion_timestamp
    FROM {{ source('debezium_women', 'inventory') }}
    {% if is_incremental() %}
    WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
    {% endif %}
)

SELECT
    *,
    CURRENT_TIMESTAMP() AS processed_at
FROM men_inventory

UNION ALL

SELECT
    *,
    CURRENT_TIMESTAMP() AS processed_at
FROM women_inventory
