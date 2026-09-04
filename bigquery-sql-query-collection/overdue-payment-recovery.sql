-- ================================================================
-- BigQuery Standard SQL
-- Fictional commerce · Overdue Subscription Payment Recovery by Day
--
-- The dataset and identifiers are fictionalized for this public example.
-- No customer-level identifiers are returned by the final aggregation.
--
-- Purpose:
--   Measure historical overdue-payment recovery behavior:
--   after a subscription billing attempt fails, how many days later
--   does the customer successfully pay?
--
-- Grain of final output:
--   due month × due week × product × cadence × recovery bucket × days overdue
--
-- Data model:
--   payments_subscriptionhistory is one row per billing attempt.
--   A failed retry and a later successful retry are separate rows.
--
-- Core joins:
--   payments_subscriptionhistory.masterid = payments_subscription.id
--   payments_subscriptionhistory.slaveid  = payments_payment.id
--
-- Billing attempt:
--   attempt_at = payments_subscriptionhistory.createddate
--
-- Successful attempt:
--   payments_subscriptionhistory.paymentsuccess IS TRUE
--   OR payments_payment.statusid IN (2, 4)
--
-- Billing cycle / recovery episode:
--   Consecutive attempts for the same subscription are grouped into one
--   cycle until the next successful attempt.
--
--   cycle_due_at:
--     first attempt timestamp in the grouped attempt sequence.
--
--   cycle_paid_at:
--     first successful attempt timestamp in the same grouped sequence.
--
-- Overdue recovered cycle:
--   A grouped attempt sequence where:
--     - at least one failed attempt occurred,
--     - a later successful attempt occurred,
--     - cycle_paid_at is after cycle_due_at by calendar day.
--
-- days_after_due:
--   DATE_DIFF(DATE(cycle_paid_at), DATE(cycle_due_at), DAY)
--
-- Cadence:
--   inferred from neighboring grouped cycles for the same subscription.
--   Prefer previous cycle distance; fallback to next cycle distance.
--
-- Scope:
--   Date range filters cycle_due_at.
--   No maximum overdue-day cap is applied.
--   Current subscription status is not used as a filter because this report
--   measures historical recovery patterns, including customers who later became
--   inactive or cancelled.
--
-- Excluded:
--   Unpaid overdue balances with no later successful recovery attempt.
-- ================================================================

DECLARE start_date DATE DEFAULT DATE '2025-01-01';
DECLARE end_date   DATE DEFAULT DATE '2025-12-31';

WITH params AS (
  SELECT
    start_date AS report_start_date,
    end_date AS report_end_date,
    TIMESTAMP(start_date) AS report_start_ts,
    TIMESTAMP(DATE_ADD(end_date, INTERVAL 1 DAY)) AS report_end_ts
),

valid_customers AS (
  SELECT
    u.id AS user_id
  FROM `portfolio_demo.identity_users` u
  WHERE u.deleted_at IS NULL
),

attempts_base AS (
  SELECT
    sh.id AS subscription_history_id,
    sh.masterid AS subscription_id,
    sh.slaveid AS payment_id,

    sh.createddate AS attempt_at,
    sh.paymentdate AS subscription_history_paymentdate,
    sh.paymentsuccess,
    sh.active AS subscription_history_active,
    sh.billingperiodspaid AS history_billingperiodspaid,

    p.statusid AS payment_statusid,
    SAFE_CAST(p.amount AS NUMERIC) AS payment_amount,
    p.createddate AS payment_createddate,
    p.updateddate AS payment_updateddate,

    CASE
      WHEN sh.paymentsuccess IS TRUE
        OR p.statusid IN (2, 4)
        THEN TRUE
      ELSE FALSE
    END AS is_successful_attempt

  FROM `portfolio_demo.payments_subscriptionhistory` sh

  LEFT JOIN `portfolio_demo.payments_payment` p
    ON p.id = sh.slaveid
   AND p.deleted_at IS NULL

  WHERE sh.masterid IS NOT NULL
    AND sh.createddate IS NOT NULL
),

attempts_with_cycle_key AS (
  SELECT
    ab.*,

    COALESCE(
      COUNTIF(is_successful_attempt) OVER (
        PARTITION BY subscription_id
        ORDER BY attempt_at, subscription_history_id
        ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
      ),
      0
    ) AS recovery_cycle_key

  FROM attempts_base ab
),

cycle_attempts AS (
  SELECT
    subscription_id,
    recovery_cycle_key,

    MIN(attempt_at) AS cycle_due_at,

    COUNT(*) AS attempt_count,
    COUNTIF(is_successful_attempt IS FALSE) AS failed_attempt_count,
    COUNTIF(is_successful_attempt IS TRUE) AS successful_attempt_count,

    STRING_AGG(
      CAST(subscription_history_id AS STRING),
      ', '
      ORDER BY attempt_at, subscription_history_id
    ) AS subscription_history_attempt_ids,

    STRING_AGG(
      CAST(payment_id AS STRING),
      ', '
      ORDER BY attempt_at, subscription_history_id
    ) AS attempted_payment_ids,

    MIN(history_billingperiodspaid) AS min_history_billingperiodspaid,
    MAX(history_billingperiodspaid) AS max_history_billingperiodspaid

  FROM attempts_with_cycle_key
  GROUP BY
    subscription_id,
    recovery_cycle_key
),

first_success_attempt AS (
  SELECT
    subscription_id,
    recovery_cycle_key,

    subscription_history_id AS paid_subscription_history_id,
    payment_id AS paid_payment_id,
    attempt_at AS cycle_paid_at,
    payment_statusid AS paid_payment_statusid,
    payment_amount AS paid_payment_amount,
    payment_createddate AS paid_payment_createddate,
    payment_updateddate AS paid_payment_updateddate

  FROM attempts_with_cycle_key

  WHERE is_successful_attempt IS TRUE

  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY subscription_id, recovery_cycle_key
    ORDER BY attempt_at, subscription_history_id
  ) = 1
),

cycles AS (
  SELECT
    ca.subscription_id,
    ca.recovery_cycle_key,

    ca.cycle_due_at,
    fsa.cycle_paid_at,

    ca.attempt_count,
    ca.failed_attempt_count,
    ca.successful_attempt_count,

    ca.subscription_history_attempt_ids,
    ca.attempted_payment_ids,

    fsa.paid_subscription_history_id,
    fsa.paid_payment_id,
    fsa.paid_payment_statusid,
    fsa.paid_payment_amount,
    fsa.paid_payment_createddate,
    fsa.paid_payment_updateddate,

    ca.min_history_billingperiodspaid,
    ca.max_history_billingperiodspaid

  FROM cycle_attempts ca

  LEFT JOIN first_success_attempt fsa
    ON fsa.subscription_id = ca.subscription_id
   AND fsa.recovery_cycle_key = ca.recovery_cycle_key
),

cycles_with_neighbors AS (
  SELECT
    c.*,

    LAG(c.cycle_due_at) OVER (
      PARTITION BY c.subscription_id
      ORDER BY c.cycle_due_at, c.recovery_cycle_key
    ) AS previous_cycle_due_at,

    LEAD(c.cycle_due_at) OVER (
      PARTITION BY c.subscription_id
      ORDER BY c.cycle_due_at, c.recovery_cycle_key
    ) AS next_cycle_due_at

  FROM cycles c
),

cycles_with_cadence AS (
  SELECT
    cwn.*,

    CASE
      WHEN cwn.previous_cycle_due_at IS NOT NULL
       AND DATE_DIFF(DATE(cwn.cycle_due_at), DATE(cwn.previous_cycle_due_at), DAY) > 0
        THEN DATE_DIFF(DATE(cwn.cycle_due_at), DATE(cwn.previous_cycle_due_at), DAY)

      WHEN cwn.next_cycle_due_at IS NOT NULL
       AND DATE_DIFF(DATE(cwn.next_cycle_due_at), DATE(cwn.cycle_due_at), DAY) > 0
        THEN DATE_DIFF(DATE(cwn.next_cycle_due_at), DATE(cwn.cycle_due_at), DAY)

      ELSE NULL
    END AS inferred_cadence_days,

    CASE
      WHEN cwn.previous_cycle_due_at IS NOT NULL
       AND DATE_DIFF(DATE(cwn.cycle_due_at), DATE(cwn.previous_cycle_due_at), DAY) > 0
        THEN 'previous_cycle_due_gap'

      WHEN cwn.next_cycle_due_at IS NOT NULL
       AND DATE_DIFF(DATE(cwn.next_cycle_due_at), DATE(cwn.cycle_due_at), DAY) > 0
        THEN 'next_cycle_due_gap'

      ELSE 'cadence_unknown'
    END AS inferred_cadence_source

  FROM cycles_with_neighbors cwn
),

overdue_recovered_cycles AS (
  SELECT
    cwc.subscription_id,
    cwc.recovery_cycle_key,

    sub.user_id,
    COALESCE(sub.productid, -1) AS product_id,
    COALESCE(pp.customkey, 'UNATTRIBUTED') AS product_sku,
    COALESCE(pp.name, 'Unattributed / Missing Product') AS product_name,

    sub.statusid AS current_subscription_statusid,
    sub.active AS current_subscription_active,
    sub.repeattypeid,
    sub.billingperiodspaid AS subscription_billingperiodspaid,
    sub.paymentduedate AS current_subscription_paymentduedate,
    sub.lastpaiddate AS current_subscription_lastpaiddate,

    cwc.cycle_due_at,
    DATE(cwc.cycle_due_at) AS due_date,
    DATE_TRUNC(DATE(cwc.cycle_due_at), WEEK(MONDAY)) AS due_week_start,
    DATE_TRUNC(DATE(cwc.cycle_due_at), MONTH) AS due_month_start,

    cwc.cycle_paid_at,
    DATE(cwc.cycle_paid_at) AS paid_date,

    cwc.previous_cycle_due_at,
    cwc.next_cycle_due_at,
    cwc.inferred_cadence_days,
    cwc.inferred_cadence_source,

    cwc.attempt_count,
    cwc.failed_attempt_count,
    cwc.successful_attempt_count,

    cwc.subscription_history_attempt_ids,
    cwc.attempted_payment_ids,

    cwc.paid_subscription_history_id,
    cwc.paid_payment_id,
    cwc.paid_payment_statusid,
    cwc.paid_payment_amount,
    cwc.paid_payment_createddate,
    cwc.paid_payment_updateddate,

    cwc.min_history_billingperiodspaid,
    cwc.max_history_billingperiodspaid,

    DATE_DIFF(DATE(cwc.cycle_paid_at), DATE(cwc.cycle_due_at), DAY)
      AS days_after_due,

    CASE
      WHEN cwc.inferred_cadence_days IS NULL
        THEN 'recovered_late_cadence_unknown'

      WHEN DATE_DIFF(DATE(cwc.cycle_paid_at), DATE(cwc.cycle_due_at), DAY)
           < cwc.inferred_cadence_days
        THEN 'recovered_before_next_expected_due'

      ELSE 'recovered_after_next_expected_due_or_multi_cycle'
    END AS recovery_timing_bucket,

    CASE
      WHEN cwc.inferred_cadence_days IS NOT NULL
       AND cwc.inferred_cadence_days > 0
        THEN DIV(
          DATE_DIFF(DATE(cwc.cycle_paid_at), DATE(cwc.cycle_due_at), DAY),
          cwc.inferred_cadence_days
        )
      ELSE NULL
    END AS estimated_full_cadence_cycles_late

  FROM cycles_with_cadence cwc

  JOIN `portfolio_demo.payments_subscription` sub
    ON sub.id = cwc.subscription_id
   AND sub.deleted_at IS NULL

  JOIN valid_customers vu
    ON vu.user_id = sub.user_id

  LEFT JOIN `portfolio_demo.products_product` pp
    ON pp.id = sub.productid

  CROSS JOIN params prm

  WHERE cwc.cycle_due_at >= prm.report_start_ts
    AND cwc.cycle_due_at <  prm.report_end_ts

    -- Recovered overdue cycles only.
    AND cwc.successful_attempt_count > 0
    AND cwc.failed_attempt_count > 0
    AND cwc.cycle_paid_at IS NOT NULL
    AND DATE(cwc.cycle_paid_at) > DATE(cwc.cycle_due_at)
),

daily_recovery_summary AS (
  SELECT
    due_month_start,
    FORMAT_DATE('%Y-%m', due_month_start) AS due_year_month,
    due_week_start,

    product_id,
    product_sku,
    product_name,

    repeattypeid,
    inferred_cadence_days,
    inferred_cadence_source,
    recovery_timing_bucket,
    estimated_full_cadence_cycles_late,

    days_after_due,

    COUNT(DISTINCT user_id) AS recovered_customer_count,
    COUNT(DISTINCT subscription_id) AS overdue_paid_subscription_count,
    COUNT(DISTINCT paid_payment_id) AS overdue_paid_payment_count,
    COUNT(*) AS overdue_paid_cycle_count,

    SUM(paid_payment_amount) AS overdue_paid_amount,
    AVG(paid_payment_amount) AS avg_overdue_paid_amount,

    AVG(attempt_count) AS avg_attempt_count_before_recovery,
    AVG(failed_attempt_count) AS avg_failed_attempt_count_before_recovery,

    MIN(due_date) AS first_due_date_in_bucket,
    MAX(due_date) AS last_due_date_in_bucket,
    MIN(paid_date) AS first_paid_date_in_bucket,
    MAX(paid_date) AS last_paid_date_in_bucket

  FROM overdue_recovered_cycles

  GROUP BY
    due_month_start,
    due_year_month,
    due_week_start,
    product_id,
    product_sku,
    product_name,
    repeattypeid,
    inferred_cadence_days,
    inferred_cadence_source,
    recovery_timing_bucket,
    estimated_full_cadence_cycles_late,
    days_after_due
)

SELECT
  due_month_start,
  due_year_month,
  due_week_start,

  product_id,
  product_sku,
  product_name,

  repeattypeid,
  inferred_cadence_days,
  inferred_cadence_source,
  recovery_timing_bucket,
  estimated_full_cadence_cycles_late,

  days_after_due,
  
  recovered_customer_count,
  overdue_paid_subscription_count,
  overdue_paid_payment_count,
  overdue_paid_cycle_count,

  overdue_paid_amount,
  avg_overdue_paid_amount,

  avg_attempt_count_before_recovery,
  avg_failed_attempt_count_before_recovery,

  ROUND(
    100 * SAFE_DIVIDE(
      overdue_paid_cycle_count,
      SUM(overdue_paid_cycle_count) OVER ()
    ),
    2
  ) AS pct_of_recovered_cycles,

  first_due_date_in_bucket,
  last_due_date_in_bucket,
  first_paid_date_in_bucket,
  last_paid_date_in_bucket

FROM daily_recovery_summary

ORDER BY
  days_after_due,
  inferred_cadence_days,
  product_name;
