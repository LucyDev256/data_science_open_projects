# BigQuery SQL Query Collection

A curated set of standalone analytical queries showing how operational data can
be converted into business-facing metrics. This is a code sample collection,
not an end-to-end data science project or a runnable copy of a production system.

The examples use BigQuery Standard SQL and demonstrate explicit grain control,
multi-stage CTE workflows, window functions, conditional aggregation, defensive
division, date spines, and documented business assumptions.

## Query index

| Query | Business question | Selected SQL patterns |
|---|---|---|
| [`daily-marketing-funnel-performance.sql`](daily-marketing-funnel-performance.sql) | How do spend, leads, bookings, purchases, revenue, and conversion rates develop by day? | Date spine, channel classification, `EXISTS`, `NOT EXISTS`, window ranking, `SAFE_DIVIDE` |
| [`overdue-payment-recovery.sql`](overdue-payment-recovery.sql) | After a failed subscription charge, how long does successful recovery take? | Episode construction, cumulative window logic, `LAG`, `LEAD`, cadence inference, recovery buckets |
| [`monthly-agent-call-performance.sql`](monthly-agent-call-performance.sql) | How do completed and missed calls and handling time vary by agent and month? | Boolean classification, `COUNTIF`, conditional duration measures, period totals with `UNION ALL` |
| [`product-sales-reporting-view.sql`](product-sales-reporting-view.sql) | How can order, payment, refund, fulfilment, and customer metrics be reported by product? | Reusable view, grain-specific facts, attribution checks, global and product rollups |

## Privacy and portability

- Company, dataset, and environment identifiers were replaced with fictional
  names; no source data, query results, credentials, customer details, or employee
  details are included.
- Customer-level identifiers were removed from the overdue-recovery output, and
  the agent report uses only a generic agent key rather than names or email.
- Table names and numeric status mappings are illustrative. They must be mapped
  to the target warehouse before use.
- Date parameters are examples, expressed as half-open windows: start date is
  inclusive and end date is exclusive.

## Adapting the examples

1. Replace the `portfolio_demo` dataset and table references.
2. Confirm the source grain and join cardinality before changing any aggregation.
3. Map product, order, payment, appointment, and call statuses to documented
   source-system values.
4. Set the reporting parameters and confirm the intended timezone.
5. Validate row counts and financial totals at every intermediate grain before
   using the results in reporting.

## Analytical boundaries

- The marketing query allocates daily spend between two conversion paths using
  the daily lead mix. This is a reporting heuristic, not user-level attribution
  or causal measurement.
- The overdue query includes only cycles that eventually recovered. Unrecovered
  balances require a separate open-balance analysis, and cadence is inferred
  from neighbouring cycle dates.
- The call report treats missing durations as zero in duration totals but excludes
  them from averages. Its missed-call definition depends on the listed statuses.
- The product view assumes one product per order. Order-created, payment-created,
  cancellation-event, and delivery-update metrics use their own event dates.
  The cancellation-to-delivery measure is an operational ratio, not customer
  churn. Consumers should apply their own `ORDER BY` when reading the view.

These boundaries are kept visible because the business meaning of a metric is as
important as the SQL that calculates it.
