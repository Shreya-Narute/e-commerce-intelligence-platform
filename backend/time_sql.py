"""Temporary: time the SQL query and K-Means separately. Delete after use."""
import sys, time
sys.path.insert(0, '/app')

from app.db.session import SessionLocal
from sqlalchemy import text
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

db = SessionLocal()
try:
    t0 = time.time()
    sql = text("""
        WITH order_payments_agg AS (
            SELECT order_id, SUM(payment_value) AS order_value
            FROM order_payments
            GROUP BY order_id
        ),
        ref AS (
            SELECT MAX(order_purchase_timestamp) + INTERVAL '1 day' AS reference_date
            FROM orders
            WHERE order_status NOT IN ('canceled', 'unavailable')
        ),
        rfm_raw AS (
            SELECT
                c.customer_unique_id,
                MAX(o.order_purchase_timestamp) AS last_purchase,
                COUNT(DISTINCT o.order_id) AS frequency,
                SUM(COALESCE(opa.order_value, 0)) AS monetary
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            LEFT JOIN order_payments_agg opa ON o.order_id = opa.order_id
            WHERE o.order_status NOT IN ('canceled', 'unavailable')
            GROUP BY c.customer_unique_id
        )
        SELECT
            r.customer_unique_id,
            EXTRACT(EPOCH FROM (ref.reference_date - r.last_purchase)) / 86400 AS recency_days,
            r.frequency,
            r.monetary,
            ref.reference_date
        FROM rfm_raw r
        CROSS JOIN ref
    """)
    rows = db.execute(sql).fetchall()
    sql_ms = int((time.time()-t0)*1000)
    print(f"SQL query: {sql_ms}ms, rows={len(rows)}")

    # DataFrame construction
    t1 = time.time()
    df = pd.DataFrame(rows, columns=["customer_unique_id", "recency_days", "frequency", "monetary", "reference_date"])
    df["recency_days"] = df["recency_days"].astype(float).round(0).astype(int)
    df_ms = int((time.time()-t1)*1000)
    print(f"DataFrame build: {df_ms}ms")

    # qcut scoring
    t2 = time.time()
    def safe_qcut(series, labels):
        try:
            return pd.qcut(series, q=5, labels=labels, duplicates="drop").astype(int)
        except Exception:
            return pd.qcut(series.rank(method="first"), q=5, labels=labels, duplicates="drop").astype(int)

    df["r_score"] = safe_qcut(df["recency_days"], [5,4,3,2,1])
    df["f_score"] = safe_qcut(df["frequency"], [1,2,3,4,5])
    df["m_score"] = safe_qcut(df["monetary"], [1,2,3,4,5])
    qcut_ms = int((time.time()-t2)*1000)
    print(f"qcut scoring: {qcut_ms}ms")

    # K-Means
    t3 = time.time()
    scaler = StandardScaler()
    features = df[["recency_days", "frequency", "monetary"]].values
    features_scaled = scaler.fit_transform(features)
    km = KMeans(n_clusters=4, random_state=42, n_init=10)
    df["cluster"] = km.fit_predict(features_scaled)
    kmeans_ms = int((time.time()-t3)*1000)
    print(f"K-Means clustering: {kmeans_ms}ms")

    total_ms = int((time.time()-t0)*1000)
    print(f"TOTAL: {total_ms}ms")
finally:
    db.close()
