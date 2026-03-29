-- Test: Verify all products have valid pricing
-- Products must have base_price > 0 and subscription_price <= base_price

SELECT
    sku,
    name,
    base_price,
    subscription_price
FROM {{ ref('silver_products') }}
WHERE base_price <= 0
   OR subscription_price > base_price
   OR subscription_price <= 0
