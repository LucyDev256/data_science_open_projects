/*
===============================================================================
CROSS-MARKET AUDIT QUERIES 
Working with the Sales Data

DATA NOTE
All markets, customers, products, dates, and commercial values in this file are
fictional and created solely for this public portfolio case study.

SQL dialect: BigQuery Standard SQL
Source table: ORDERS
Source grain: one row per order line

WORKFLOW
1. Keep only genuine charged purchases: pv > 0.
2. Aggregate order lines to order level before sequencing customer orders.
3. Calculate 2026 product-line sales and percentage shares. (Part A)
4. Rank orders to identify each customer's first order. (Part B)
5. Identify the second order and calculate the elapsed days. (Part C)
6. Validate totals, customer counts, and averages.

ASSUMPTIONS
- Each order_id belongs to one customer, date, and product line.
- If two orders have the same date, the lower order_id is treated as earlier
  because no order timestamp is available.
- Customers without a second order are excluded from the average return time.
- Business interpretations are descriptive because the sample has only six
  customers.
===============================================================================
*/

-- Create the fictional sample as a temporary table.
-- Run this complete file as a BigQuery multi-statement script or in a session.
CREATE TEMP TABLE ORDERS (
  order_id INT64,
  customer_id INT64,
  order_date DATE,
  market STRING,
  sku STRING,
  product_line STRING,
  pv NUMERIC,
  sales_value NUMERIC
);

INSERT INTO ORDERS VALUES
  (1,  1001, DATE '2025-03-11', 'Market A', 'Seed-A', 'SeedProduct', 45,  120),
  (2,  1001, DATE '2026-01-15', 'Market A', 'Seed-A', 'SeedProduct', 50,  140),
  (3,  1001, DATE '2026-03-08', 'Market A', 'Seed-B', 'SeedProduct', 60,  180),
  (4,  1002, DATE '2026-02-15', 'Market A', 'Nut-2', 'NutProduct',   130, 650),
  (5,  1002, DATE '2026-04-20', 'Market A', 'Seed-A', 'SeedProduct', 45, 120),
  (6,  1003, DATE '2026-03-05', 'Market B',  'Seed-A', 'SeedProduct', 45, 110),
  (7,  1004, DATE '2026-03-02', 'Market A', 'Nut-1', 'NutProduct',   120, 600),
  (8,  1004, DATE '2026-03-20', 'Market A', 'Seed-A', 'SeedProduct', 50, 140),
  (9,  1004, DATE '2026-05-10', 'Market A', 'Nut-2', 'NutProduct',   130, 650),
  (10, 1005, DATE '2025-11-05', 'Market B',  'Seed-A', 'SeedProduct', 45, 115),
  (11, 1005, DATE '2026-02-19', 'Market B',  'Seed-B', 'SeedProduct', 60, 180),
  (12, 1005, DATE '2026-03-27', 'Market B',  'Fruit-3', 'FruitProduct',   30, 95),
  (13, 1006, DATE '2026-01-10', 'Market A', 'Nut-1', 'NutProduct',   120, 600),
  (14, 1006, DATE '2026-06-14', 'Market A', 'Nut-1', 'NutProduct',   120, 600);

-- =============================================================================
-- PART A — 2026 sales and percentage share by product line
-- =============================================================================
-- Method:
-- 1. Sum sales within calendar year 2026.
-- 2. Divide each product-line total by total 2026 sales.

WITH product_line_sales AS (
  SELECT
    product_line,
    SUM(sales_value) AS total_sales

  FROM `ORDERS`

  WHERE pv > 0
    AND order_date >= DATE '2026-01-01'
    AND order_date <  DATE '2027-01-01'

  GROUP BY
    product_line
)

SELECT
  product_line,
  total_sales,
  ROUND(
    100 * SAFE_DIVIDE(
      total_sales,
      SUM(total_sales) OVER ()
    ),
    2
  ) AS share_of_2026_sales_pct

FROM product_line_sales

ORDER BY
  total_sales DESC;

/*
RESULT

product_line	total_sales	share_of_2026_sales_pct
NutProduct	      3100	      76.26
SeedProduct	    870	        21.4
FruitProduct	    95	        2.34

BUSINESS INTERPRETATION
NutProduct generated 76.26% of 2026 sales in this sample, making it the main
sales contributor.
*/


-- =============================================================================
-- PART B — First-ever order for each customer
-- =============================================================================
-- Method:
-- 1. Aggregate lines to one row per order.
-- 2. Rank each customer's orders chronologically.

WITH order_level AS (
  SELECT
    order_id,
    customer_id,
    order_date,
    product_line AS business_line,
    SUM(sales_value) AS order_value

  FROM `ORDERS`

  WHERE pv > 0

  GROUP BY
    order_id,
    customer_id,
    order_date,
    product_line
)

SELECT
  customer_id,
  order_date AS first_order_date,
  business_line,
  order_value AS first_order_value

FROM order_level

QUALIFY ROW_NUMBER() OVER (
  PARTITION BY customer_id
  ORDER BY order_date, order_id
) = 1

ORDER BY
  customer_id;

/*
RESULT

customer_id	first_order_date	business_line	first_order_value
1001	      2025-03-11	      SeedProduct	    120
1002	      2026-02-15	      NutProduct	      650
1003	      2026-03-05	      SeedProduct	    110
1004	      2026-03-02	      NutProduct	      600
1005	      2025-11-05	      SeedProduct	    115
1006	      2026-01-10	      NutProduct	      600

BUSINESS INTERPRETATION
SeedProduct and NutProduct were equally common entry business lines in this sample,
with three customers starting in each.
*/


-- =============================================================================
-- PART C — Days between first and second order
-- =============================================================================
-- Method:
-- 1. Keep genuine purchases (pv > 0) and aggregate order lines to order level.
-- 2. Sequence each customer's orders using order_date and order_id.
-- 3. Use LEAD(order_date) to obtain the following order date.
-- 4. The first query shows the first-to-second-order interval for each customer.
-- 5. The second query groups those results by the first-purchased product line.
-- 6. COUNTIF counts customers with a second order, while AVG ignores NULL values.

-- Part C1 — Customer-level result - supporting overview query
WITH order_level AS (
  SELECT
    order_id,
    customer_id,
    order_date,
    product_line,
    SUM(sales_value) AS order_value
  FROM `ORDERS`
  WHERE pv > 0
  GROUP BY
    order_id,
    customer_id,
    order_date,
    product_line
),

sequenced_orders AS (
  SELECT
    order_id,
    customer_id,
    order_date,
    product_line,

    ROW_NUMBER() OVER (
      PARTITION BY customer_id
      ORDER BY order_date, order_id
    ) AS order_number,

    LEAD(order_date) OVER (
      PARTITION BY customer_id
      ORDER BY order_date, order_id
    ) AS second_order_date

  FROM order_level
)

SELECT
  customer_id,
  product_line AS first_product_line,
  order_date AS first_order_date,
  second_order_date,
  DATE_DIFF(
    second_order_date,
    order_date,
    DAY
  ) AS days_to_second_order

FROM sequenced_orders

WHERE order_number = 1

ORDER BY customer_id;

/*
customer_id	first_product_line	first_order_date	second_order_date	days_to_second_order
1001	      SeedProduct	          2025-03-11	      2026-01-15	      310
1002	      NutProduct	            2026-02-15	      2026-04-20	      64
1003	      SeedProduct	          2026-03-05		
1004	      NutProduct	            2026-03-02	      2026-03-20	      18
1005	      SeedProduct	          2025-11-05	      2026-02-19	      106
1006	      NutProduct	            2026-01-10	      2026-06-14	      155

*/


--Part C2 — Aggregated results - requested results

WITH order_level AS (
  SELECT
    order_id,
    customer_id,
    order_date,
    product_line,
    SUM(sales_value) AS order_value
  FROM `ORDERS`
  WHERE pv > 0
  GROUP BY
    order_id,
    customer_id,
    order_date,
    product_line
),

sequenced_orders AS (
  SELECT
    order_id,
    customer_id,
    order_date,
    product_line,

    ROW_NUMBER() OVER (
      PARTITION BY customer_id
      ORDER BY order_date, order_id
    ) AS order_number,

    LEAD(order_date) OVER (
      PARTITION BY customer_id
      ORDER BY order_date, order_id
    ) AS second_order_date

  FROM order_level
),

first_orders AS (
  SELECT
    customer_id,
    product_line AS first_product_line,
    second_order_date,

    DATE_DIFF(
      second_order_date,
      order_date,
      DAY
    ) AS days_to_second_order

  FROM sequenced_orders

  WHERE order_number = 1
)

SELECT
  first_product_line,

  COUNTIF(
    second_order_date IS NOT NULL
  ) AS customers_with_second_order,

  ROUND(
    AVG(days_to_second_order),
    1
  ) AS avg_days_to_second_order

FROM first_orders

GROUP BY first_product_line

ORDER BY avg_days_to_second_order;

/*
AGGREGATED RESULT

first_product_line	customers_with_second_order	avg_days_to_second_order
NutProduct	            3	                          79.0
SeedProduct	          2	                          208.0

VALIDATION
- NutProduct average:   (64 + 18 + 155) / 3 = 79 days.
- SeedProduct average: (310 + 106) / 2 = 208 days.

*/

-- BUSINESS INTERPRETATION:
-- NutProduct-first customers placed their second order sooner on average than
-- SeedProduct-first customers (79 versus 208 days), suggesting faster repeat
-- purchasing in this small sample.


/*
===============================================================================
SHORT WRITTEN SUMMARY

In 2026, the sample generated $4,065 in sales. NutProduct contributed $3,100
(76.26%), SeedProduct $870 (21.40%), and FruitProduct $95 (2.34%). The six customers
were evenly split between NutProduct and SeedProduct as their first-purchased
business line. All three NutProduct-first customers placed a second order, taking
79 days on average; two SeedProduct-first customers returned, taking 208 days on
average. This suggests that NutProduct-first customers came back sooner in this
sample, although the result is descriptive and based on very few customers.
===============================================================================
*/
