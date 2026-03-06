-- Silver Layer: Unified Product Catalog
-- Cleaned and validated product data from both brands

{{ config(
    materialized='table',
    tags=['silver', 'pharmaceutical']
) }}

WITH men_products AS (
    SELECT * FROM {{ ref('bronze_men_products') }}
),

women_products AS (
    SELECT * FROM {{ ref('bronze_women_products') }}
),

unified_products AS (
    -- Men's health products
    SELECT
        'mens' AS brand,
        id AS product_id,
        sku,
        name AS product_name,
        category AS product_category,
        description,
        
        -- Parse JSON for active ingredients
        JSON_EXTRACT_SCALAR(active_ingredients, '$[0].name') AS primary_ingredient,
        active_ingredients AS ingredient_details,
        
        dosage_form,
        strength,
        requires_dea,
        fda_approved,
        ndc_code,
        
        -- Pricing
        CAST(base_price AS NUMERIC) AS base_price,
        CAST(subscription_price AS NUMERIC) AS subscription_price,
        insurance_coverable,
        
        -- Status
        is_active,
        created_at,
        updated_at
    FROM men_products
    
    UNION ALL
    
    -- Women's health products
    SELECT
        'womens' AS brand,
        id AS product_id,
        sku,
        name AS product_name,
        category AS product_category,
        description,
        JSON_EXTRACT_SCALAR(active_ingredients, '$[0].name') AS primary_ingredient,
        active_ingredients AS ingredient_details,
        dosage_form,
        strength,
        requires_dea,
        fda_approved,
        ndc_code,
        CAST(base_price AS NUMERIC) AS base_price,
        CAST(subscription_price AS NUMERIC) AS subscription_price,
        insurance_coverable,
        is_active,
        created_at,
        updated_at
    FROM women_products
)

SELECT
    {{ dbt_utils.surrogate_key(['brand', 'product_id']) }} AS product_key,
    *,
    
    -- Data quality flags
    CASE 
        WHEN base_price IS NULL THEN 'missing_price'
        WHEN base_price < 0 THEN 'invalid_price'
        ELSE 'valid'
    END AS price_quality_flag,
    
    CASE
        WHEN fda_approved = FALSE AND requires_dea = TRUE THEN 'review_required'
        ELSE 'ok'
    END AS compliance_flag,
    
    CURRENT_TIMESTAMP() AS processed_at
    
FROM unified_products

-- Data quality tests
WHERE sku IS NOT NULL
  AND product_name IS NOT NULL
  AND base_price >= 0
