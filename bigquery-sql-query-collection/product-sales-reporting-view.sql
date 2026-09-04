-- BigQuery Standard SQL
-- Product-level order, payment, and fulfilment reporting view
--
-- The dataset and identifiers are fictionalized for this public example.
-- Replace the reporting window and status mappings before adapting the view.
-- The single-product-per-order rule below is an explicit source-system assumption.

CREATE OR REPLACE VIEW `portfolio_demo.sales_product_split_report_view` AS
WITH
  -------------------------------------------------------------------
  -- 1. REPORTING WINDOW
  -------------------------------------------------------------------
  params AS (
    SELECT
      DATE '2025-01-01' AS report_start_date,
      DATE '2025-02-01' AS report_end_date -- exclusive
  ),

  -------------------------------------------------------------------
  -- 2. BASE ORDERS
  -------------------------------------------------------------------
  orders AS (
    SELECT
      so.id AS order_id,
      so.user_id,
      so.statusid AS order_statusid,
      so.createddate,
      SAFE_CAST(so.subtotaldiscounts AS NUMERIC) AS subtotaldiscounts
    FROM `portfolio_demo.ordering_salesorder` so
    CROSS JOIN params p
    WHERE DATE(so.createddate) >= p.report_start_date
      AND DATE(so.createddate) <  p.report_end_date
      AND so.statusid NOT IN (13, 21)
  ),

  -------------------------------------------------------------------
  -- 3. BASE PAYMENTS
  -------------------------------------------------------------------
  payments AS (
    SELECT
      p.id AS payment_id,
      p.statusid AS payment_statusid,
      SAFE_CAST(p.amount AS NUMERIC) AS amount,
      p.createddate,
      p.updateddate
    FROM `portfolio_demo.payments_payment` p
    CROSS JOIN params r
    WHERE DATE(p.createddate) >= r.report_start_date
      AND DATE(p.createddate) <  r.report_end_date
  ),

  -------------------------------------------------------------------
  -- 4. PRODUCT DESCRIPTION
  -------------------------------------------------------------------
  product_descr AS (
    SELECT
      p.id        AS product_id,
      p.name      AS product_name,
      p.customkey AS product_sku
    FROM `portfolio_demo.products_product` p
  ),

  -------------------------------------------------------------------
  -- 5. FILTERED ORDER PRODUCT FACT
  --    One order always contains one product.
  --    Used for order-created-in-period product metrics.
  -------------------------------------------------------------------
  order_product_fact AS (
    SELECT
      o.order_id,
      o.user_id,
      o.order_statusid,
      o.createddate,
      o.subtotaldiscounts,

      pd.product_name,
      pd.product_sku,

      SUM(SAFE_CAST(soi.quantity AS NUMERIC)) AS total_order_quantity,

      SUM(
        SAFE_CAST(soi.quantity AS NUMERIC)
        * SAFE_CAST(soi.unitsoldprice AS NUMERIC)
      ) AS total_order_revenue
    FROM orders o
    JOIN `portfolio_demo.ordering_salesorderitem` soi
      ON soi.masterid = o.order_id
    JOIN product_descr pd
      ON pd.product_id = soi.productid
    GROUP BY
      o.order_id,
      o.user_id,
      o.order_statusid,
      o.createddate,
      o.subtotaldiscounts,
      pd.product_name,
      pd.product_sku
  ),

  -------------------------------------------------------------------
  -- 6. ALL ORDER PRODUCT MAP
  --    Used for payment/status attribution.
  --    Not filtered by order createddate.
  -------------------------------------------------------------------
  order_product_map_all AS (
    SELECT DISTINCT
      soi.masterid AS order_id,
      pd.product_name,
      pd.product_sku
    FROM `portfolio_demo.ordering_salesorderitem` soi
    JOIN product_descr pd
      ON pd.product_id = soi.productid
  ),

  -------------------------------------------------------------------
  -- 7. PAYMENT EVENTS WITH PRODUCT ATTRIBUTION
  --    If payment cannot be mapped to a product, it is under 'Unmapped / Unknown Product'.
  -------------------------------------------------------------------
  payment_events_attributed AS (
    SELECT
      sop.masterid AS order_id,

      COALESCE(opm.product_name, 'Unmapped / Unknown Product') AS product_name,
      COALESCE(opm.product_sku,  'unmapped') AS product_sku,

      p.payment_id,
      p.payment_statusid,
      p.amount,

      CASE
        WHEN sop.slaveid IS NULL THEN 'missing_salesorderpayment_map'
        WHEN opm.order_id IS NULL THEN 'missing_order_product_map'
        ELSE 'attributed_to_product'
      END AS attribution_status
    FROM payments p
    LEFT JOIN `portfolio_demo.payments_salesorderpayment` sop
      ON sop.slaveid = p.payment_id
    LEFT JOIN order_product_map_all opm
      ON opm.order_id = sop.masterid
  ),

  -------------------------------------------------------------------
  -- 8. PRODUCT PAYMENT METRICS
  -------------------------------------------------------------------
  product_payment_metrics AS (
    SELECT
      product_name,
      product_sku,

      ROUND(
        SUM(CASE WHEN payment_statusid IN (2, 4) THEN amount ELSE 0 END),
        2
      ) AS gross_revenue,

      ROUND(
        SUM(CASE WHEN payment_statusid IN (2, 4) THEN amount ELSE 0 END)
        -
        SUM(CASE WHEN payment_statusid = 6 THEN amount ELSE 0 END),
        2
      ) AS net_revenue,

      COUNTIF(payment_statusid IN (2, 4)) AS total_transactions,

      COUNTIF(payment_statusid = 6) AS refund_count,

      ROUND(
        SUM(CASE WHEN payment_statusid = 6 THEN amount ELSE 0 END),
        0
      ) AS refund_amount,

      COUNTIF(payment_statusid = 5) AS void_count,

      ROUND(
        SUM(CASE WHEN payment_statusid = 5 THEN amount ELSE 0 END),
        2
      ) AS void_amount
    FROM payment_events_attributed
    GROUP BY
      product_name,
      product_sku
  ),

  -------------------------------------------------------------------
  -- 9. PRODUCT ORDER METRICS
  --    Unmapped payment row has no order metrics unless the order itself exists in the order/product fact.
  -------------------------------------------------------------------
  product_order_metrics AS (
    SELECT
      product_name,
      product_sku,

      COUNT(DISTINCT order_id) AS total_orders,
      COUNT(DISTINCT user_id)  AS unique_customers,

      SUM(total_order_quantity) AS total_order_quantity,

      ROUND(
        SUM(total_order_revenue),
        2
      ) AS total_order_revenue,

      COUNT(DISTINCT CASE
        WHEN order_statusid IN (9, 10)
        THEN order_id
      END) AS shipped_orders,

      ROUND(
        SUM(subtotaldiscounts),
        2
      ) AS discount_amount
    FROM order_product_fact
    GROUP BY
      product_name,
      product_sku
  ),

  -------------------------------------------------------------------
  -- 10. CANCELED / DELIVERED ORDER SETS
  -------------------------------------------------------------------
  canceled_orders AS (
    SELECT DISTINCT
      oa.order_id
    FROM `portfolio_demo.ordering_order_activities` oa
    CROSS JOIN params p
    WHERE oa.activity_type = 'cancelled'
      AND oa.deleted_at IS NULL
      AND DATE(oa.created_at) >= p.report_start_date
      AND DATE(oa.created_at) <  p.report_end_date
  ),

  delivered_orders AS (
    SELECT
      so.id AS order_id
    FROM `portfolio_demo.ordering_salesorder` so
    CROSS JOIN params p
    WHERE so.statusid = 12
      AND DATE(so.updateddate) >= p.report_start_date
      AND DATE(so.updateddate) <  p.report_end_date
  ),

  -------------------------------------------------------------------
  -- 11. PRODUCT STATUS METRICS
  --     Canceled/delivered counts are also mapped to Unknown if the order cannot be mapped to a product.
  -------------------------------------------------------------------
  product_status_metrics AS (
    SELECT
      product_name,
      product_sku,

      COUNT(DISTINCT CASE WHEN status_metric = 'canceled'  THEN order_id END) AS canceled_orders,
      COUNT(DISTINCT CASE WHEN status_metric = 'delivered' THEN order_id END) AS delivered_orders
    FROM (
      SELECT
        COALESCE(opm.product_name, 'Unmapped / Unknown Product') AS product_name,
        COALESCE(opm.product_sku,  'unmapped') AS product_sku,
        co.order_id,
        'canceled' AS status_metric
      FROM canceled_orders co
      LEFT JOIN order_product_map_all opm
        ON opm.order_id = co.order_id

      UNION ALL

      SELECT
        COALESCE(opm.product_name, 'Unmapped / Unknown Product') AS product_name,
        COALESCE(opm.product_sku,  'unmapped') AS product_sku,
        d.order_id,
        'delivered' AS status_metric
      FROM delivered_orders d
      LEFT JOIN order_product_map_all opm
        ON opm.order_id = d.order_id
    )
    GROUP BY
      product_name,
      product_sku
  ),

  -------------------------------------------------------------------
  -- 12. PRODUCT KEYS
  --     Ensures Unmapped / Unknown Product appears when it has payment or status activity.
  -------------------------------------------------------------------
  product_keys AS (
    SELECT product_name, product_sku FROM product_order_metrics
    UNION DISTINCT
    SELECT product_name, product_sku FROM product_payment_metrics
    UNION DISTINCT
    SELECT product_name, product_sku FROM product_status_metrics
  ),

  -------------------------------------------------------------------
  -- 13. FINAL PRODUCT METRICS
  -------------------------------------------------------------------
  product_metrics AS (
    SELECT
      pk.product_name,
      pk.product_sku,

      IFNULL(pom.total_order_quantity, 0) AS total_order_quantity,
      IFNULL(pom.total_order_revenue, 0)  AS total_order_revenue,

      IFNULL(ppm.gross_revenue, 0) AS gross_revenue,
      IFNULL(ppm.net_revenue, 0)   AS net_revenue,

      IFNULL(
        ROUND(
          SAFE_DIVIDE(
            IFNULL(ppm.gross_revenue, 0),
            NULLIF(IFNULL(pom.total_orders, 0), 0)
          ),
          0
        ),
        0
      ) AS avg_order_value,

      IFNULL(pom.shipped_orders, 0) AS shipped_orders,
      IFNULL(psm.canceled_orders, 0) AS canceled_orders,

      IFNULL(pom.unique_customers, 0) AS unique_customers,

      IFNULL(ppm.total_transactions, 0) AS total_transactions,
      IFNULL(ppm.refund_count, 0)       AS refund_count,
      IFNULL(ppm.refund_amount, 0)      AS refund_amount,
      IFNULL(ppm.void_count, 0)         AS void_count,
      IFNULL(ppm.void_amount, 0)        AS void_amount,

      IFNULL(pom.discount_amount, 0) AS discount_amount,

      IFNULL(
        ROUND(
          SAFE_DIVIDE(
            IFNULL(psm.canceled_orders, 0),
            NULLIF(IFNULL(psm.delivered_orders, 0), 0)
          ),
          2
        ),
        0
      ) AS cancellation_to_delivery_ratio
    FROM product_keys pk
    LEFT JOIN product_order_metrics pom
      USING (product_name, product_sku)
    LEFT JOIN product_payment_metrics ppm
      USING (product_name, product_sku)
    LEFT JOIN product_status_metrics psm
      USING (product_name, product_sku)
  ),

  -------------------------------------------------------------------
  -- 14. GLOBAL ORDER METRICS
  -------------------------------------------------------------------
  global_order_metrics AS (
    SELECT
      COUNT(DISTINCT order_id) AS total_orders,
      COUNT(DISTINCT user_id)  AS unique_customers,

      COUNT(DISTINCT CASE
        WHEN order_statusid IN (9, 10)
        THEN order_id
      END) AS shipped_orders,

      SUM(total_order_quantity) AS total_order_quantity,

      ROUND(
        SUM(total_order_revenue),
        2
      ) AS total_order_revenue,

      ROUND(
        SUM(subtotaldiscounts),
        2
      ) AS discount_amount
    FROM order_product_fact
  ),

  -------------------------------------------------------------------
  -- 15. GLOBAL PAYMENT METRICS
  -------------------------------------------------------------------
  global_payment_metrics AS (
    SELECT
      ROUND(
        SUM(CASE WHEN payment_statusid IN (2, 4) THEN amount ELSE 0 END),
        2
      ) AS gross_revenue,

      ROUND(
        SUM(CASE WHEN payment_statusid = 6 THEN amount ELSE 0 END),
        0
      ) AS refund_amount,

      ROUND(
        SUM(CASE WHEN payment_statusid IN (2, 4) THEN amount ELSE 0 END)
        -
        SUM(CASE WHEN payment_statusid = 6 THEN amount ELSE 0 END),
        2
      ) AS net_revenue,

      COUNTIF(payment_statusid IN (2, 4)) AS total_transactions,
      COUNTIF(payment_statusid = 6)       AS refund_count,
      COUNTIF(payment_statusid = 5)       AS void_count,

      ROUND(
        SUM(CASE WHEN payment_statusid = 5 THEN amount ELSE 0 END),
        2
      ) AS void_amount
    FROM payments
  ),

  -------------------------------------------------------------------
  -- 16. GLOBAL STATUS METRICS
  -------------------------------------------------------------------
  global_status_metrics AS (
    SELECT
      (SELECT COUNT(*) FROM canceled_orders)  AS canceled_orders,
      (SELECT COUNT(*) FROM delivered_orders) AS delivered_orders
  ),

  -------------------------------------------------------------------
  -- 17. FINAL GLOBAL METRICS
  -------------------------------------------------------------------
  global_metrics AS (
    SELECT
      gom.total_order_quantity,
      gom.total_order_revenue,

      gpm.gross_revenue,
      gpm.net_revenue,

      ROUND(
        SAFE_DIVIDE(
          gpm.gross_revenue,
          NULLIF(gom.total_orders, 0)
        ),
        0
      ) AS avg_order_value,

      gom.shipped_orders,
      gsm.canceled_orders,
      gom.unique_customers,

      gpm.total_transactions,
      gpm.refund_count,
      gpm.refund_amount,
      gpm.void_count,
      gpm.void_amount,

      gom.discount_amount,

      ROUND(
        SAFE_DIVIDE(
          gsm.canceled_orders,
          NULLIF(gsm.delivered_orders, 0)
        ),
        2
      ) AS cancellation_to_delivery_ratio
    FROM global_order_metrics gom
    CROSS JOIN global_payment_metrics gpm
    CROSS JOIN global_status_metrics gsm
  )

-------------------------------------------------------------------
-- 18. FINAL OUTPUT
-------------------------------------------------------------------
SELECT
  'all' AS product_name,
  'na'  AS product_sku,
  gm.total_order_quantity,
  gm.total_order_revenue,
  gm.gross_revenue,
  gm.net_revenue,
  gm.avg_order_value,
  gm.shipped_orders,
  gm.canceled_orders,
  ROUND(gm.unique_customers, 0)               AS unique_customers,
  ROUND(gm.total_transactions, 0)             AS total_transactions,
  gm.refund_count,
  ROUND(CAST(gm.refund_amount AS NUMERIC), 0) AS refund_amount,
  gm.void_count,
  gm.void_amount,
  gm.discount_amount,
  gm.cancellation_to_delivery_ratio
FROM global_metrics gm

UNION ALL

SELECT
  pm.product_name,
  pm.product_sku,
  pm.total_order_quantity,
  pm.total_order_revenue,
  pm.gross_revenue,
  pm.net_revenue,
  pm.avg_order_value,
  pm.shipped_orders,
  pm.canceled_orders,
  ROUND(CAST(pm.unique_customers AS NUMERIC), 0)   AS unique_customers,
  ROUND(CAST(pm.total_transactions AS NUMERIC), 0) AS total_transactions,
  pm.refund_count,
  ROUND(CAST(pm.refund_amount AS NUMERIC), 0) AS refund_amount,
  pm.void_count,
  pm.void_amount,
  pm.discount_amount,
  pm.cancellation_to_delivery_ratio
FROM product_metrics pm;
