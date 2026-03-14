-- Test: Ensure DEA-required products have proper tracking
-- Products requiring DEA should have requires_dea = TRUE and valid ndc_code

SELECT
    sku,
    name,
    category,
    requires_dea,
    ndc_code
FROM {{ ref('silver_products') }}
WHERE category IN ('HORMONE_THERAPY', 'CONTROLLED_SUBSTANCE')
  AND (requires_dea = FALSE OR ndc_code IS NULL OR LENGTH(ndc_code) < 10)
