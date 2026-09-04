-- BigQuery Standard SQL
-- Daily marketing and conversion-funnel performance
--
-- Final grain: one row per calendar date.
-- The dataset and identifiers are fictionalized for this public example.
-- Replace the parameters and status mappings before adapting the query.

WITH

params AS (
  SELECT
    DATE '2025-01-01' AS report_start_date,
    DATE '2025-02-01' AS report_end_date, -- exclusive
    1001 AS target_product_id
),

-- ─── 1. Facebook: daily spend and engagement by campaign ─────────────────────
meta_campaigns AS (
  SELECT
    date,
    campaign_name,
    LOWER(campaign_name) LIKE '%schedule%'  AS is_schedule_campaign,
    SUM(spend)               AS spend,
    SUM(impressions)         AS impressions,
    SUM(clicks)              AS clicks,
    SUM(link_clicks)         AS link_clicks,
    SUM(landing_page_views)  AS lpv,
    SUM(purchase_value)      AS purchase_value,
    SUM(landing_page_views)  AS landing_page_views
  FROM `portfolio_demo.fb_ad_spend`
  CROSS JOIN params p
  WHERE date >= p.report_start_date
    AND date <  p.report_end_date
  GROUP BY date, campaign_name
),

meta_daily AS (
  SELECT
    date,
    SUM(spend)                                      AS total_spend,
    SUM(IF(    is_schedule_campaign, spend, 0))      AS schedule_spend,
    SUM(IF(NOT is_schedule_campaign, spend, 0))      AS purchase_spend,
    SUM(impressions)                                AS total_impressions,
    SUM(clicks)                                     AS total_clicks,
    SUM(link_clicks)                                AS total_link_clicks, --equal to clicks if no social engagement (likes, shares, comments) and only platform destination
    SUM(lpv)                                        AS total_lpv,
    SUM(purchase_value)                             AS fb_purchase_value,
    SUM(landing_page_views)                         AS fb_landing_page_views
  FROM meta_campaigns
  GROUP BY date
),

-- ─── 2. Leads: new prospect accounts, split by ever-booked status ─────────────
booked_users AS (
  SELECT DISTINCT patient_user_id
  FROM `portfolio_demo.scheduling_scheduled_appointments`
  WHERE appointment_type = 'customer_intake'
    AND deleted_at IS NULL
    --AND status != 'cancelled'
),

leads_daily AS (
  SELECT
    DATE(u.created_at)                   AS date,
    COUNT(*)                             AS total_leads,
    COUNT(bu.patient_user_id)            AS leads_with_booking,
    COUNTIF(bu.patient_user_id IS NULL)  AS leads_without_booking,
    COUNTIF(
      LOWER(u.utm_source) LIKE '%meta%'
      OR LOWER(u.utm_source) LIKE '%facebook%'
      OR LOWER(u.landing_page) LIKE '%fbclid%'
    )  AS meta_leads,
    COUNTIF(
      LOWER(u.landing_page) LIKE '%gclid%'
      OR LOWER(u.landing_page) LIKE '%gad_source%'
      OR LOWER(u.utm_source) LIKE '%google%'
    )  AS google_leads,
    COUNTIF(
      NOT COALESCE(
        LOWER(u.utm_source) LIKE '%meta%'
        OR LOWER(u.utm_source) LIKE '%facebook%'
        OR LOWER(u.landing_page) LIKE '%fbclid%'
        OR LOWER(u.landing_page) LIKE '%gclid%'
        OR LOWER(u.landing_page) LIKE '%gad_source%'
        OR LOWER(u.utm_source) LIKE '%google%',
        FALSE
      )
    )  AS organic_leads
  FROM `portfolio_demo.identity_users` u
  LEFT JOIN booked_users bu ON bu.patient_user_id = u.id
  CROSS JOIN params p
  WHERE u.user_type_id IN (6, 7)
    AND u.deleted_at IS NULL
    AND DATE(u.created_at) >= p.report_start_date
    AND DATE(u.created_at) <  p.report_end_date
  GROUP BY date
),

-- ─── 3. Direct purchases: first in-window target-product order per user ───────
direct_purchases_raw AS (
  SELECT
    so.user_id,
    so.createddate,
    CAST(so.total AS FLOAT64) AS total,
    ROW_NUMBER() OVER (
      PARTITION BY so.user_id
      ORDER BY so.createddate, so.id
    ) AS rn
  FROM `portfolio_demo.ordering_salesorder` so
  CROSS JOIN params p
  WHERE CAST(so.total AS FLOAT64) > 0
    AND so.subscription_id IS NULL
    AND DATE(so.createddate) >= p.report_start_date
    AND DATE(so.createddate) <  p.report_end_date
    AND EXISTS (
      SELECT 1 FROM `portfolio_demo.ordering_salesorderitem` soi
      WHERE soi.masterid = so.id
        AND soi.productid = p.target_product_id
    )
    AND NOT EXISTS (
      SELECT 1 FROM booked_users bu
      WHERE bu.patient_user_id = so.user_id
    )
),

direct_purchases_daily AS (
  SELECT
    DATE(createddate)  AS date,
    COUNT(*)           AS direct_purchases,
    SUM(total)         AS direct_revenue
  FROM direct_purchases_raw
  WHERE rn = 1
  GROUP BY date
),

-- ─── 4. Bookings: new customer_intake appointments per day ────────────────────
bookings_daily AS (
  SELECT
    DATE(created_at)                  AS date,
    COUNT(DISTINCT patient_user_id)   AS bookings
  FROM `portfolio_demo.scheduling_scheduled_appointments`
  CROSS JOIN params p
  WHERE appointment_type = 'customer_intake'
    AND deleted_at IS NULL
    --AND status != 'cancelled'
    AND DATE(created_at) >= p.report_start_date
    AND DATE(created_at) <  p.report_end_date
  GROUP BY date
),

-- ─── 5. Booking conversions: booked users (in window) who also purchased ──────
booking_users_in_window AS (
  SELECT
    patient_user_id,
    MIN(created_at) AS first_booking_at
  FROM `portfolio_demo.scheduling_scheduled_appointments`
  CROSS JOIN params p
  WHERE appointment_type = 'customer_intake'
    AND deleted_at IS NULL
    --AND status != 'cancelled'
    AND DATE(created_at) >= p.report_start_date
    AND DATE(created_at) <  p.report_end_date
  GROUP BY patient_user_id
),

booking_with_first_purchase AS (
  SELECT
    bw.patient_user_id,
    bw.first_booking_at,
    MIN(so.createddate) AS first_purchase_at
  FROM booking_users_in_window bw
  CROSS JOIN params p
  JOIN `portfolio_demo.ordering_salesorder` so
    ON so.user_id = bw.patient_user_id
   AND CAST(so.total AS FLOAT64) > 0
   AND so.subscription_id IS NULL
   AND so.createddate >= bw.first_booking_at
  JOIN `portfolio_demo.ordering_salesorderitem` soi
    ON soi.masterid = so.id
   AND soi.productid = p.target_product_id
  GROUP BY bw.patient_user_id, bw.first_booking_at
),

booking_conversions_daily AS (
  SELECT
    DATE(first_booking_at)                                                     AS date,
    COUNT(*)                                                                   AS booking_conversions,
    AVG(TIMESTAMP_DIFF(first_purchase_at, first_booking_at, SECOND) / 86400.0) AS avg_days_to_purchase
  FROM booking_with_first_purchase
  GROUP BY DATE(first_booking_at)
),

-- ─── Date spine ───────────────────────────────────────────────────────────────
date_spine AS (
  SELECT date
  FROM params p
  CROSS JOIN UNNEST(
    GENERATE_DATE_ARRAY(
      p.report_start_date,
      DATE_SUB(p.report_end_date, INTERVAL 1 DAY)
    )
  ) AS date
)

SELECT
  d.date,

  -- Spend (Meta)
  ROUND(IFNULL(m.total_spend,       0), 2)  AS total_ad_spend,
  ROUND(IFNULL(m.purchase_spend,    0), 2)  AS abo_trt_purchase_spend,
  ROUND(IFNULL(m.schedule_spend,    0), 2)  AS abo_trt_schedule_spend,

  -- Meta engagement
  IFNULL(m.total_impressions,  0)  AS total_impressions,
  IFNULL(m.total_clicks,       0)  AS total_clicks,
  IFNULL(m.total_link_clicks,  0)  AS total_link_clicks,
  IFNULL(m.total_lpv,          0)  AS total_lpv,
  ROUND(IFNULL(m.fb_purchase_value,  0), 2)  AS fb_purchase_value,
  IFNULL(m.fb_landing_page_views, 0) AS fb_landing_page_views,
  ROUND(SAFE_DIVIDE(
    IFNULL(m.fb_purchase_value, 0),
    NULLIF(IFNULL(m.total_spend, 0), 0)
  ), 2)                            AS roas,
  ROUND(SAFE_DIVIDE(
    IFNULL(p.direct_revenue, 0),
    NULLIF(IFNULL(m.total_spend, 0), 0)
  ), 2)                            AS db_roas, -- using the db data
  ROUND(SAFE_DIVIDE(
    IFNULL(m.total_spend, 0) * 1000,
    NULLIF(IFNULL(m.total_impressions, 0), 0)
  ), 2)                            AS cpm,
  ROUND(SAFE_DIVIDE(
    IFNULL(m.total_clicks, 0),
    NULLIF(IFNULL(m.total_impressions, 0), 0)
  ), 4)                            AS ctr,
  ROUND(SAFE_DIVIDE(
    IFNULL(m.total_spend, 0),
    NULLIF(IFNULL(m.total_clicks, 0), 0)
  ), 2)                            AS cpc,

  -- Leads (DB)
  IFNULL(l.total_leads,            0)  AS leads,
  IFNULL(l.leads_with_booking,     0)  AS leads_with_booking,
  IFNULL(l.leads_without_booking,  0)  AS leads_without_booking,
  IFNULL(l.meta_leads,             0)  AS meta_leads,
  IFNULL(l.google_leads,           0)  AS google_leads,
  IFNULL(l.organic_leads,          0)  AS organic_leads,

  -- Direct purchase funnel (DB)
  IFNULL(p.direct_purchases,  0)  AS direct_purchases,
  ROUND(IFNULL(p.direct_revenue,    0), 2)  AS direct_revenue,
  ROUND(SAFE_DIVIDE(
    IFNULL(m.total_spend, 0) * IFNULL(l.leads_without_booking, 0),
    NULLIF(IFNULL(l.total_leads, 0) * IFNULL(p.direct_purchases, 0), 0)
  ), 2)                           AS cost_per_purchase,
  ROUND(SAFE_DIVIDE(
    IFNULL(p.direct_purchases,             0),
    NULLIF(IFNULL(l.leads_without_booking, 0), 0)
  ), 4)                           AS direct_purchase_conversion_rate,

  -- Booking funnel (DB)
  IFNULL(b.bookings, 0)           AS bookings,
  ROUND(SAFE_DIVIDE(
    IFNULL(m.total_spend, 0) * IFNULL(l.leads_with_booking, 0),
    NULLIF(IFNULL(l.total_leads, 0) * IFNULL(b.bookings, 0), 0)
  ), 2)                           AS cost_per_booking,
  IFNULL(bc.booking_conversions, 0)  AS booking_conversions,
  ROUND(SAFE_DIVIDE(
    IFNULL(bc.booking_conversions, 0),
    NULLIF(IFNULL(b.bookings,      0), 0)
  ), 4)                           AS booking_conversion_rate,
  ROUND(bc.avg_days_to_purchase, 2) AS avg_days_to_purchase

FROM date_spine d
LEFT JOIN meta_daily                m  ON m.date  = d.date
LEFT JOIN leads_daily               l  ON l.date  = d.date
LEFT JOIN direct_purchases_daily    p  ON p.date  = d.date
LEFT JOIN bookings_daily            b  ON b.date  = d.date
LEFT JOIN booking_conversions_daily bc ON bc.date = d.date
ORDER BY d.date;
