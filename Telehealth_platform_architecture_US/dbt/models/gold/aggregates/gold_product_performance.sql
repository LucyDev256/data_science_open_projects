-- Gold Layer: Product Performance Dashboard
-- Dimensional model for product analytics

{{ config(
    materialized='table',
    tags=['gold', 'analytics', 'dashboard']
) }}

WITH products AS (
    SELECT * FROM {{ ref('silver_products') }}
),

orders AS (
    SELECT * FROM {{ ref('silver_orders') }}
),

inventory AS (
    SELECT * FROM {{ ref('silver_inventory') }}
),

prescriptions AS (
    SELECT
        product_id,
        COUNT(*) AS prescription_count,
        COUNT(CASE WHEN status = 'APPROVED' THEN 1 END) AS approved_count,
        COUNT(CASE WHEN status = 'DENIED' THEN 1 END) AS denied_count
    FROM {{ ref('silver_prescriptions') }}
    GROUP BY product_id
),

revenue AS (
    SELECT
        oli.product_id,
        SUM(oli.subtotal) AS total_revenue,
        COUNT(DISTINCT o.order_id) AS order_count,
        SUM(oli.quantity) AS units_sold
    FROM {{ ref('silver_order_line_items') }} oli
    JOIN orders o ON oli.order_id = o.order_id
    WHERE o.status NOT IN ('CANCELLED', 'REFUNDED')
    GROUP BY oli.product_id
),

current_inventory AS (
    SELECT
        product_id,
        SUM(quantity_available) AS total_available,
        SUM(quantity_reserved) AS total_reserved,
        MIN(expiration_date) AS earliest_expiration
    FROM inventory
    WHERE expiration_date > CURRENT_DATE()
    GROUP BY product_id
)

SELECT
    -- Product dimensions
    p.product_key,
    p.brand,
    p.product_id,
    p.sku,
    p.product_name,
    p.product_category,
    p.primary_ingredient,
    p.dosage_form,
    p.requires_dea,
    
    -- Pricing
    p.base_price,
    p.subscription_price,
    CASE 
        WHEN p.subscription_price IS NOT NULL 
        THEN ROUND((p.base_price - p.subscription_price) / p.base_price * 100, 2)
        ELSE 0
    END AS subscription_discount_pct,
    
    -- Performance metrics
    COALESCE(r.total_revenue, 0) AS lifetime_revenue,
    COALESCE(r.order_count, 0) AS total_orders,
    COALESCE(r.units_sold, 0) AS total_units_sold,
    
    CASE 
        WHEN r.units_sold > 0 
        THEN ROUND(r.total_revenue / r.units_sold, 2)
        ELSE p.base_price
    END AS avg_revenue_per_unit,
    
    -- Prescription metrics
    COALESCE(pr.prescription_count, 0) AS total_prescriptions,
    COALESCE(pr.approved_count, 0) AS approved_prescriptions,
    COALESCE(pr.denied_count, 0) AS denied_prescriptions,
    
    CASE 
        WHEN pr.prescription_count > 0 
        THEN ROUND(pr.approved_count / pr.prescription_count * 100, 2)
        ELSE NULL
    END AS approval_rate_pct,
    
    -- Inventory status
    COALESCE(i.total_available, 0) AS current_stock_level,
    COALESCE(i.total_reserved, 0) AS reserved_stock,
    i.earliest_expiration,
    
    CASE
        WHEN i.total_available = 0 THEN 'out_of_stock'
        WHEN i.total_available < 50 THEN 'low_stock'
        WHEN i.earliest_expiration <= DATE_ADD(CURRENT_DATE(), INTERVAL 30 DAY) THEN 'expiring_soon'
        ELSE 'in_stock'
    END AS inventory_status,
    
    -- Product health score (0-100)
    ROUND(
        (COALESCE(pr.approved_count, 0) * 0.4 +  -- 40% weight on approvals
         LEAST(COALESCE(r.units_sold, 0), 100) * 0.3 +  -- 30% weight on sales (capped at 100)
         CASE WHEN i.total_available > 0 THEN 30 ELSE 0 END),  -- 30% weight on availability
        0
    ) AS product_health_score,
    
    -- Status flags
    p.is_active,
    p.compliance_flag,
    
    CURRENT_TIMESTAMP() AS last_updated

FROM products p
LEFT JOIN prescriptions pr ON p.product_id = pr.product_id
LEFT JOIN revenue r ON p.product_id = r.product_id
LEFT JOIN current_inventory i ON p.product_id = i.product_id

WHERE p.is_active = TRUE
