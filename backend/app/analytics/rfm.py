
"""
RFM Segmentation Analytics
===========================
Computes Recency / Frequency / Monetary scores per customer_unique_id,
applies rule-based segment labels, and runs K-Means clustering.

Results are cached in-process for 1 hour to avoid repeated heavy computation.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sqlalchemy import text
from sqlalchemy.orm import Session

# ---------------------------------------------------------------------------
# In-memory cache {key: {"timestamp": float, "data": Any}}
# ---------------------------------------------------------------------------
_CACHE: Dict[str, Dict[str, Any]] = {}
_CACHE_TTL = 3600


def _get_cached(key: str) -> Optional[Any]:
    entry = _CACHE.get(key)
    if entry and (time.time() - entry["timestamp"]) < _CACHE_TTL:
        return entry["data"]
    return None


def _set_cached(key: str, data: Any) -> None:
    _CACHE[key] = {"timestamp": time.time(), "data": data}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def compute_rfm(db: Session) -> Dict[str, Any]:
    """Return the full RFM result, cached for one hour."""
    cached = _get_cached("rfm")
    if cached is not None:
        return cached

    result = _compute_rfm_uncached(db)

    if result.get("status") == "ok":
        _set_cached("rfm", result)

    return result


# ---------------------------------------------------------------------------
# Core computation
# ---------------------------------------------------------------------------
def _compute_rfm_uncached(db: Session) -> Dict[str, Any]:
    sql = text(
        """
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
            EXTRACT(EPOCH FROM (ref.reference_date - r.last_purchase))
                / 86400 AS recency_days,
            r.frequency,
            r.monetary,
            ref.reference_date
        FROM rfm_raw r
        CROSS JOIN ref
        """
    )

    rows = db.execute(sql).fetchall()

    if not rows:
        return {
            "status": "no_data",
            "message": "Dataset not loaded.",
            "data": [],
        }

    df = pd.DataFrame(
        rows,
        columns=[
            "customer_unique_id",
            "recency_days",
            "frequency",
            "monetary",
            "reference_date",
        ],
    )

    df["recency_days"] = (
        df["recency_days"].astype(float).round(0).astype(int)
    )
    df["frequency"] = df["frequency"].astype(int)
    df["monetary"] = pd.to_numeric(
        df["monetary"], errors="coerce"
    ).fillna(0.0)

    reference_date = pd.to_datetime(df["reference_date"].iloc[0])
    rfm = df.drop(columns=["reference_date"]).copy()

    if len(rfm) < 10:
        return {
            "status": "insufficient_data",
            "message": "Fewer than 10 customers found. Cannot compute RFM.",
            "data": [],
        }

    # ------------------------------------------------------------------
    # RFM scores (1-5)
    # Use rank-based quintiles to handle duplicate values safely.
    # ------------------------------------------------------------------
    def safe_qcut(series: pd.Series, labels: list) -> pd.Series:
        ranked = series.rank(method="first")
        return pd.qcut(
            ranked,
            q=5,
            labels=labels,
        ).astype(int)

    rfm["r_score"] = safe_qcut(
        rfm["recency_days"], labels=[5, 4, 3, 2, 1]
    )
    rfm["f_score"] = safe_qcut(
        rfm["frequency"], labels=[1, 2, 3, 4, 5]
    )
    rfm["m_score"] = safe_qcut(
        rfm["monetary"], labels=[1, 2, 3, 4, 5]
    )

    # ------------------------------------------------------------------
    # Segment labels (vectorized instead of row-by-row apply)
    # ------------------------------------------------------------------
    r = rfm["r_score"]
    f = rfm["f_score"]

    conditions = [
        (r >= 4) & (f >= 4),
        (r >= 3) & (f >= 3),
        (r <= 2) & (f >= 3),
        (r == 1) & (f <= 2),
        (f == 1) & (r >= 4),
        (r >= 3) & (f == 2),
    ]

    choices = [
        "Champions",
        "Loyal Customers",
        "At Risk",
        "Lost",
        "New Customers",
        "Potential Loyalists",
    ]

    rfm["segment"] = np.select(
        conditions,
        choices,
        default="Others",
    )

    # ------------------------------------------------------------------
    # K-Means clustering (k=4)
    # ------------------------------------------------------------------
    features = rfm[
        ["recency_days", "frequency", "monetary"]
    ].copy()

    features_scaled = StandardScaler().fit_transform(features)

    km = KMeans(
        n_clusters=4,
        random_state=42,
        n_init=10,
    )
    rfm["cluster"] = km.fit_predict(features_scaled)

    # ------------------------------------------------------------------
    # Approximate silhouette score using a deterministic sample.
    # Full-data silhouette scoring is too expensive for large datasets.
    # ------------------------------------------------------------------
    sil_score: Optional[float] = None

    if rfm["cluster"].nunique() > 1:
        try:
            sample_size = min(2000, len(rfm))

            sil_score = float(
                silhouette_score(
                    features_scaled,
                    rfm["cluster"],
                    sample_size=sample_size,
                    random_state=42,
                )
            )
        except Exception:
            sil_score = None

    # ------------------------------------------------------------------
    # Segment summaries
    # ------------------------------------------------------------------
    segments_df = (
        rfm.groupby("segment")
        .agg(
            customer_count=("customer_unique_id", "count"),
            avg_recency_days=("recency_days", "mean"),
            avg_frequency=("frequency", "mean"),
            avg_monetary=("monetary", "mean"),
        )
        .reset_index()
    )

    segments = [
        {
            "segment": row["segment"],
            "customer_count": int(row["customer_count"]),
            "avg_recency_days": round(
                float(row["avg_recency_days"]), 1
            ),
            "avg_frequency": round(
                float(row["avg_frequency"]), 2
            ),
            "avg_monetary": round(
                float(row["avg_monetary"]), 2
            ),
        }
        for _, row in segments_df.iterrows()
    ]

    # ------------------------------------------------------------------
    # Score distribution
    # ------------------------------------------------------------------
    score_dist = [
        {
            "score": score_val,
            "r_count": int((rfm["r_score"] == score_val).sum()),
            "f_count": int((rfm["f_score"] == score_val).sum()),
            "m_count": int((rfm["m_score"] == score_val).sum()),
        }
        for score_val in range(1, 6)
    ]

    # ------------------------------------------------------------------
    # Cluster sizes
    # ------------------------------------------------------------------
    cluster_sizes = {
        str(k): int(v)
        for k, v in rfm["cluster"].value_counts().to_dict().items()
    }

    # ------------------------------------------------------------------
    # Customer records
    # ------------------------------------------------------------------
    customer_columns = [
        "customer_unique_id",
        "recency_days",
        "frequency",
        "monetary",
        "r_score",
        "f_score",
        "m_score",
        "segment",
        "cluster",
    ]

    customers = rfm[customer_columns].copy()
    customers["monetary"] = customers["monetary"].round(2)

    integer_columns = [
        "recency_days",
        "frequency",
        "r_score",
        "f_score",
        "m_score",
        "cluster",
    ]

    customers[integer_columns] = customers[integer_columns].astype(int)

    customers_list = customers.to_dict(orient="records")

    return {
        "status": "ok",
        "message": "",
        "reference_date": reference_date.date().isoformat(),
        "total_customers": len(rfm),
        "silhouette_score": (
            round(sil_score, 4)
            if sil_score is not None
            else None
        ),
        "cluster_sizes": cluster_sizes,
        "segments": segments,
        "score_distribution": score_dist,
        "customers": customers_list,
    }
