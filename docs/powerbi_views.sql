-- =============================================================================
-- Power BI Analytical Views
-- E-Commerce Intelligence & Decision Support Platform (Brazilian Olist dataset)
-- =============================================================================
--
-- Purpose:
--   Read-only PostgreSQL views that mirror the FastAPI analytics services so
--   Power BI Desktop can build dashboards directly against the database without
--   going through the REST API.
--
-- IMPORTANT - data availability:
--   These views return EMPTY result sets until the Olist CSV files have been
--   ingested into PostgreSQL (see scripts/ingest_data.py). With no data loaded
--   every SELECT against a view returns zero rows - this is expected, not an
--   error. Do NOT fabricate sample rows.
--
-- IMPORTANT - source of truth:
--   The Python analytics layer (backend/app/analytics/*.py, especially rfm.py)
--   is the authoritative implementation for RFM scoring, K-Means clustering and
--   segment labelling. The SQL views below are a Power BI-facing mirror that
--   approximates the same logic with native PostgreSQL window functions. For
--   exact parity with the API responses (e.g. K-Means cluster ids, cache, the
--   <10-customer "insufficient_data" guard) use the REST endpoints, not these
--   views.
--
-- Table/column names follow backend/app/models/olist.py exactly.
-- Run order: execute this whole file once (psql -f docs/powerbi_views.sql or
-- pgAdmin query tool). All statements are idempotent (CREATE OR REPLACE).
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 1) vw_sales_monthly
--    Monthly revenue, order count and average order value for DELIVERED orders.
--    Revenue = SUM(order_payments.payment_value).
--    Mirrors backend/app/services/sales_service.get_monthly_revenue (which does
--    not filter on status) - this view restricts to delivered orders per the
--    Power BI requirement.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_sales_monthly AS
SELECT
    to_char(o.order_purchase_timestamp, 'YYYY-MM') AS year_month,
    SUM(op.payment_value) AS revenue,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(op.payment_value) / NULLIF(COUNT(DISTINCT o.order_id), 0) AS avg_order_value
FROM orders o
JOIN order_payments op ON o.order_id = op.order_id
WHERE o.order_status = 'delivered'
GROUP BY to_char(o.order_purchase_timestamp, 'YYYY-MM')
ORDER BY year_month;


-- -----------------------------------------------------------------------------
-- 2) vw_product_performance
--    One row per product: total revenue (SUM order_items.price), order count,
--    average item price. Category falls back to the English translation, then
--    the original Portuguese name, then 'unknown'.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_product_performance AS
SELECT
    p.product_id,
    COALESCE(pct.product_category_name_english, p.product_category_name, 'unknown') AS category,
    SUM(oi.price) AS total_revenue,
    COUNT(DISTINCT oi.order_id) AS order_count,
    AVG(oi.price) AS avg_price
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN product_category_translation pct
    ON p.product_category_name = pct.product_category_name
GROUP BY
    p.product_id,
    COALESCE(pct.product_category_name_english, p.product_category_name, 'unknown');


-- -----------------------------------------------------------------------------
-- 3) vw_customer_rfm
--    Recency / Frequency / Monetary scoring per customer_unique_id using
--    PostgreSQL NTILE(5) quintiles, plus a rule-based segment label.
--
--    Recency (days)   = (reference_date - last_purchase), reference_date is
--                       MAX(order_purchase_timestamp) + 1 day across all orders.
--    R_score          = NTILE(5) ORDER BY recency_days DESC  (fewer days -> 5).
--    F_score          = NTILE(5) ORDER BY frequency ASC      (more orders -> 5).
--    M_score          = NTILE(5) ORDER BY monetary ASC      (more spend -> 5).
--    segment          = CASE that mirrors rfm._label() exactly.
--
--    Excludes orders with status 'canceled' or 'unavailable', matching rfm.py.
--    NOTE: NTILE evenly buckets rows; the Python code uses pandas.qcut with
--    duplicates='drop', so scores can differ slightly when many customers share
--    identical R/F/M values. The API (app.analytics.rfm) remains authoritative.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_customer_rfm AS
WITH rfm_base AS (
    SELECT
        c.customer_unique_id,
        MAX(o.order_purchase_timestamp) AS last_purchase,
        COUNT(DISTINCT o.order_id) AS frequency,
        SUM(op.payment_value) AS monetary
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_payments op ON o.order_id = op.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY c.customer_unique_id
),
ref AS (
    SELECT (MAX(order_purchase_timestamp) + INTERVAL '1 day')::timestamp AS ref_date
    FROM orders
),
rfm_calc AS (
    SELECT
        b.customer_unique_id,
        EXTRACT(EPOCH FROM ((SELECT ref_date FROM ref) - b.last_purchase)) / 86400.0 AS recency_days,
        b.frequency,
        b.monetary
    FROM rfm_base b
),
scored AS (
    SELECT
        customer_unique_id,
        recency_days,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC)    AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC)     AS m_score
    FROM rfm_calc
)
SELECT
    customer_unique_id,
    ROUND(recency_days::numeric, 1) AS recency_days,
    frequency,
    ROUND(monetary::numeric, 2) AS monetary,
    r_score,
    f_score,
    m_score,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score = 1  AND f_score <= 2 THEN 'Lost'
        WHEN f_score = 1  AND r_score >= 4 THEN 'New Customers'
        WHEN r_score >= 3 AND f_score = 2  THEN 'Potential Loyalists'
        ELSE 'Others'
    END AS segment
FROM scored;


-- -----------------------------------------------------------------------------
-- 4) vw_seller_performance
--    One row per seller: state, total revenue (SUM order_items.price), order
--    count and average review score. Reviews are LEFT JOINed through orders so
--    sellers whose orders have no review still appear (avg_review_score NULL).
--    avg_review_score is weighted by order-item rows (an order with several
--    items from the same seller contributes its score once per item).
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_seller_performance AS
SELECT
    s.seller_id,
    s.seller_state,
    SUM(oi.price) AS total_revenue,
    COUNT(DISTINCT oi.order_id) AS order_count,
    AVG(rev.review_score) AS avg_review_score
FROM sellers s
JOIN order_items oi ON s.seller_id = oi.seller_id
JOIN orders o        ON oi.order_id = o.order_id
LEFT JOIN order_reviews rev ON o.order_id = rev.order_id
GROUP BY s.seller_id, s.seller_state;


-- -----------------------------------------------------------------------------
-- 5) vw_delivery_performance
--    One row per delivered order: customer state, delivery_days
--    (delivered_customer_date - purchase_timestamp), on_time flag
--    (delivered <= estimated), and the order review score (LEFT JOIN so orders
--    without a review still appear with review_score NULL).
--    Restricted to orders that actually have a delivered_customer_date.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_delivery_performance AS
SELECT
    o.order_id,
    c.customer_state,
    ROUND((EXTRACT(EPOCH FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 86400.0)::numeric, 1) AS delivery_days,
    (o.order_delivered_customer_date <= o.order_estimated_delivery_date) AS on_time,
    rev.review_score
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN order_reviews rev ON o.order_id = rev.order_id
WHERE o.order_delivered_customer_date IS NOT NULL;
