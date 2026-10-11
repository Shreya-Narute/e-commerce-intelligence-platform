"""
Payment Analytics Service
==========================
Provides payment summaries, installment distributions, and monthly volumes.
"""

from typing import Any, Dict
from sqlalchemy import func, distinct, case
from sqlalchemy.orm import Session

from app.models.olist import Order, OrderPayment

_NO_DATA_MSG = "Dataset not loaded. Please ingest the Olist CSV data first."


def _has_payments(db: Session) -> bool:
    return db.query(func.count(OrderPayment.order_id)).scalar() > 0


def get_payment_summary(db: Session) -> Dict[str, Any]:
    if not _has_payments(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": {}}

    summary_row = db.query(
        func.sum(OrderPayment.payment_value).label("total_value"),
        func.avg(OrderPayment.payment_installments).label("avg_installments"),
    ).one()

    type_rows = (
        db.query(
            OrderPayment.payment_type.label("payment_type"),
            func.sum(OrderPayment.payment_value).label("total_value"),
            func.count(OrderPayment.payment_sequential).label("transaction_count"),
        )
        .group_by(OrderPayment.payment_type)
        .order_by(func.sum(OrderPayment.payment_value).desc())
        .all()
    )

    payment_type_breakdown = [
        {
            "payment_type": r.payment_type,
            "total_value": round(float(r.total_value), 2),
            "transaction_count": int(r.transaction_count),
        }
        for r in type_rows
    ]

    return {
        "status": "ok",
        "message": "",
        "data": {
            "total_payment_value": round(float(summary_row.total_value or 0), 2),
            "avg_installments": round(float(summary_row.avg_installments), 2) if summary_row.avg_installments else None,
            "payment_type_breakdown": payment_type_breakdown,
        },
    }


def get_installment_distribution(db: Session) -> Dict[str, Any]:
    if not _has_payments(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    rows = (
        db.query(
            OrderPayment.payment_installments.label("installments"),
            func.count(OrderPayment.payment_sequential).label("count"),
        )
        .group_by(OrderPayment.payment_installments)
        .order_by(OrderPayment.payment_installments)
        .all()
    )

    # Bucket 12+ together
    bucketed: Dict[str, int] = {}
    for r in rows:
        inst = int(r.installments)
        key = str(inst) if inst < 12 else "12+"
        bucketed[key] = bucketed.get(key, 0) + int(r.count)

    # Sort: numeric keys first, then "12+"
    def sort_key(k: str):
        return (1, int(k)) if k != "12+" else (2, 99)

    data = [
        {"installments": k, "count": bucketed[k]}
        for k in sorted(bucketed.keys(), key=sort_key)
    ]
    return {"status": "ok", "message": "", "data": data}


def get_monthly_volume(db: Session) -> Dict[str, Any]:
    if not _has_payments(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    rows = (
        db.query(
            func.to_char(Order.order_purchase_timestamp, "YYYY-MM").label("year_month"),
            func.sum(OrderPayment.payment_value).label("total_value"),
            func.count(OrderPayment.payment_sequential).label("transaction_count"),
        )
        .join(Order, OrderPayment.order_id == Order.order_id)
        .group_by(func.to_char(Order.order_purchase_timestamp, "YYYY-MM"))
        .order_by(func.to_char(Order.order_purchase_timestamp, "YYYY-MM"))
        .all()
    )

    data = [
        {
            "year_month": r.year_month,
            "total_value": round(float(r.total_value), 2),
            "transaction_count": int(r.transaction_count),
        }
        for r in rows
    ]
    return {"status": "ok", "message": "", "data": data}
