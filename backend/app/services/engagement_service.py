"""
Customer Engagement Risk Service
==================================
Rule-based engagement risk classification using recency ONLY.
This is NOT ML churn prediction.

Tiers (relative to max(order_purchase_timestamp) in dataset):
  Active        : last purchase within 90 days
  Cooling       : 91-180 days since last purchase
  At Risk       : 181-365 days
  Inactive      : > 365 days
"""

from typing import Any, Dict
from sqlalchemy import func, text
from sqlalchemy.orm import Session

_NO_DATA_MSG = "Dataset not loaded. Please ingest the Olist CSV data first."

_TIER_DESCRIPTIONS = {
    "Active": "Purchased within the last 90 days.",
    "Cooling": "No purchase for 91–180 days. May need re-engagement.",
    "At Risk": "No purchase for 181–365 days. High disengagement risk.",
    "Inactive": "No purchase for over 365 days. Likely churned.",
}


def _classify_tier(days: int) -> str:
    if days <= 90:
        return "Active"
    if days <= 180:
        return "Cooling"
    if days <= 365:
        return "At Risk"
    return "Inactive"


def get_risk_summary(db: Session) -> Dict[str, Any]:
    sql = text(
        """
        SELECT
            c.customer_unique_id,
            MAX(o.order_purchase_timestamp) AS last_purchase
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_unique_id
        """
    )
    rows = db.execute(sql).fetchall()

    if not rows:
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    import pandas as pd

    df = pd.DataFrame(rows, columns=["customer_unique_id", "last_purchase"])
    df["last_purchase"] = pd.to_datetime(df["last_purchase"])

    reference_date = df["last_purchase"].max()
    df["days_since"] = (reference_date - df["last_purchase"]).dt.days
    df["tier"] = df["days_since"].apply(_classify_tier)

    counts = df["tier"].value_counts().to_dict()
    tiers_order = ["Active", "Cooling", "At Risk", "Inactive"]

    data = [
        {
            "tier": tier,
            "customer_count": int(counts.get(tier, 0)),
            "description": _TIER_DESCRIPTIONS[tier],
        }
        for tier in tiers_order
    ]

    return {
        "status": "ok",
        "message": "",
        "reference_date": reference_date.date().isoformat(),
        "data": data,
    }


def get_at_risk_customers(db: Session, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
    sql = text(
        """
        SELECT
            c.customer_unique_id,
            MAX(o.order_purchase_timestamp) AS last_purchase
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_unique_id
        """
    )
    rows = db.execute(sql).fetchall()

    if not rows:
        return {"status": "no_data", "message": _NO_DATA_MSG, "total": 0, "page": page, "page_size": page_size, "data": []}

    import pandas as pd

    df = pd.DataFrame(rows, columns=["customer_unique_id", "last_purchase"])
    df["last_purchase"] = pd.to_datetime(df["last_purchase"])

    reference_date = df["last_purchase"].max()
    df["days_since"] = (reference_date - df["last_purchase"]).dt.days
    df["tier"] = df["days_since"].apply(_classify_tier)

    at_risk_df = df[df["tier"].isin(["At Risk", "Inactive"])].copy()
    at_risk_df = at_risk_df.sort_values("days_since", ascending=False)

    total = len(at_risk_df)
    offset = (page - 1) * page_size
    page_df = at_risk_df.iloc[offset : offset + page_size]

    data = [
        {
            "customer_unique_id": row["customer_unique_id"],
            "last_purchase_date": row["last_purchase"].date().isoformat(),
            "days_since_purchase": int(row["days_since"]),
            "tier": row["tier"],
        }
        for _, row in page_df.iterrows()
    ]

    return {
        "status": "ok",
        "message": "",
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": data,
    }
