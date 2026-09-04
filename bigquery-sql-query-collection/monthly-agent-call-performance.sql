-- BigQuery Standard SQL
-- Monthly voice-call performance by support agent
--
-- Final grain: one row per agent and calendar month, plus one period-total row
-- per agent. The dataset and identifiers are fictionalized for this example.

WITH
  params AS (
    SELECT
      DATE '2025-01-01' AS start_date,
      DATE '2025-04-01' AS end_date -- exclusive
  ),

  base_calls AS (
    SELECT
      t.id,
      t.direction,
      t.voice_status,
      t.initiated_at,
      t.agent_user_id,
      t.call_duration_seconds
    FROM `portfolio_demo.communications_communication_logs` t
    CROSS JOIN params p
    WHERE
      t.deleted_at IS NULL
      AND t.channel = 'voice'
      AND t.initiated_at >= TIMESTAMP(p.start_date)
      AND t.initiated_at <  TIMESTAMP(p.end_date)
  ),

  classified_calls AS (
    SELECT
      *,

      direction = 'outbound'
      AND voice_status = 'completed' AS is_outbound_completed,

      direction = 'inbound'
      AND voice_status = 'completed' AS is_inbound_completed,

      direction = 'inbound'
      AND voice_status IN ('no_answer', 'failed', 'busy', 'canceled') AS is_missed

    FROM base_calls
  ),

  period_agent_totals AS (
    SELECT
      'TOTAL' AS calendar_month,
      CAST(t.agent_user_id AS STRING) AS agent_user_id,

      COUNT(*) AS total_calls,

      COUNTIF(t.is_outbound_completed) AS outbound_calls,

      COUNTIF(t.is_inbound_completed) AS inbound_calls,

      COUNTIF(t.is_missed) AS missed_calls,

      COUNTIF(
        t.is_outbound_completed
        OR t.is_inbound_completed
      ) AS completed_calls,

      SUM(IF(
        t.is_outbound_completed,
        COALESCE(t.call_duration_seconds, 0),
        0
      )) AS outbound_call_duration_seconds,

      SUM(IF(
        t.is_inbound_completed,
        COALESCE(t.call_duration_seconds, 0),
        0
      )) AS inbound_call_duration_seconds,

      SUM(IF(
        t.is_missed,
        COALESCE(t.call_duration_seconds, 0),
        0
      )) AS missed_call_duration_seconds,

      SUM(IF(
        t.is_outbound_completed OR t.is_inbound_completed,
        COALESCE(t.call_duration_seconds, 0),
        0
      )) AS completed_call_duration_seconds,

      ROUND(AVG(IF(
        t.is_outbound_completed,
        t.call_duration_seconds,
        NULL
      )), 2) AS avg_outbound_call_duration_seconds,

      ROUND(AVG(IF(
        t.is_inbound_completed,
        t.call_duration_seconds,
        NULL
      )), 2) AS avg_inbound_call_duration_seconds,

      ROUND(AVG(IF(
        t.is_outbound_completed OR t.is_inbound_completed,
        t.call_duration_seconds,
        NULL
      )), 2) AS avg_completed_call_duration_seconds

    FROM classified_calls t
    GROUP BY
      agent_user_id
  ),

  monthly_agent_results AS (
    SELECT
      FORMAT_DATE('%Y-%m', DATE_TRUNC(DATE(t.initiated_at), MONTH)) AS calendar_month,
      CAST(t.agent_user_id AS STRING) AS agent_user_id,

      COUNT(*) AS total_calls,

      COUNTIF(t.is_outbound_completed) AS outbound_calls,

      COUNTIF(t.is_inbound_completed) AS inbound_calls,

      COUNTIF(t.is_missed) AS missed_calls,

      COUNTIF(
        t.is_outbound_completed
        OR t.is_inbound_completed
      ) AS completed_calls,

      SUM(IF(
        t.is_outbound_completed,
        COALESCE(t.call_duration_seconds, 0), --Replaces missing duration values (NULL) with 0. may re reversed to NULL depending on the business logic
        0
      )) AS outbound_call_duration_seconds,

      SUM(IF(
        t.is_inbound_completed,
        COALESCE(t.call_duration_seconds, 0),
        0
      )) AS inbound_call_duration_seconds,

      SUM(IF(
        t.is_missed,
        COALESCE(t.call_duration_seconds, 0),
        0
      )) AS missed_call_duration_seconds,

      SUM(IF(
        t.is_outbound_completed OR t.is_inbound_completed,
        COALESCE(t.call_duration_seconds, 0),
        0
      )) AS completed_call_duration_seconds,

      ROUND(AVG(IF(
        t.is_outbound_completed,
        t.call_duration_seconds,
        NULL
      )), 2) AS avg_outbound_call_duration_seconds,

      ROUND(AVG(IF(
        t.is_inbound_completed,
        t.call_duration_seconds,
        NULL
      )), 2) AS avg_inbound_call_duration_seconds,

      ROUND(AVG(IF(
        t.is_outbound_completed OR t.is_inbound_completed,
        t.call_duration_seconds,
        NULL
      )), 2) AS avg_completed_call_duration_seconds

    FROM classified_calls t
    GROUP BY
      calendar_month,
      agent_user_id
  )

SELECT
  calendar_month,
  agent_user_id,

  total_calls,
  outbound_calls,
  inbound_calls,
  missed_calls,
  completed_calls,

  outbound_call_duration_seconds,
  inbound_call_duration_seconds,
  missed_call_duration_seconds,
  completed_call_duration_seconds,

  avg_outbound_call_duration_seconds,
  avg_inbound_call_duration_seconds,
  avg_completed_call_duration_seconds

FROM period_agent_totals

UNION ALL

SELECT
  calendar_month,
  agent_user_id,

  total_calls,
  outbound_calls,
  inbound_calls,
  missed_calls,
  completed_calls,

  outbound_call_duration_seconds,
  inbound_call_duration_seconds,
  missed_call_duration_seconds,
  completed_call_duration_seconds,

  avg_outbound_call_duration_seconds,
  avg_inbound_call_duration_seconds,
  avg_completed_call_duration_seconds

FROM monthly_agent_results

ORDER BY
  CASE WHEN calendar_month = 'TOTAL' THEN 0 ELSE 1 END,
  calendar_month,
  agent_user_id;
