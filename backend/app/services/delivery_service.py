"""
Delivery & Satisfaction Analytics Service
==========================================
Only considers orders where order_delivered_customer_date IS NOT NULL
and order_status = 'delivered'.
"""

from typing import Any, Dict
from sqlalchemy import func, distinct, case
from sqlalchemy.orm import Session

from app.models.olist import Order, OrderReview, Customer

_NO_DATA_MSG = "Dataset not loaded. Please ingest the Olist CSV data first."


def _has_delivered_orders(db: Session) -> bool:
    return (
        db.query(func.count(Order.order_id))
        .filter(
            Order.order_delivered_customer_date.isnot(None),
            Order.order_status == "delivered",
        )
        .scalar()
        > 0
    )


def get_delivery_summary(db: Session) -> Dict[str, Any]:
    if not _has_delivered_orders(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": {}}

    row = (
        db.query(
            func.avg(
                func.extract(
                    "epoch",
                    Order.order_delivered_customer_date - Order.order_purchase_timestamp,
                )
                / 86400.0
            ).label("avg_delivery_days"),
            func.avg(
                case(
                    (
                        Order.order_delivered_customer_date <= Order.order_estimated_delivery_date,
                        1.0,
                    ),
                    else_=0.0,
                )
            ).label("on_time_rate"),
            func.count(Order.order_id).label("total_delivered"),
        )
        .filter(
            Order.order_delivered_customer_date.isnot(None),
            Order.order_status == "delivered",
        )
        .one()
    )

    # Avg review score for delivered orders
    review_row = (
        db.query(func.avg(OrderReview.review_score).label("avg_score"))
        .join(Order, OrderReview.order_id == Order.order_id)
        .filter(
            Order.order_delivered_customer_date.isnot(None),
            Order.order_status == "delivered",
        )
        .one()
    )

    return {
        "status": "ok",
        "message": "",
        "data": {
            "avg_delivery_days": round(float(row.avg_delivery_days), 1) if row.avg_delivery_days else None,
            "on_time_rate": round(float(row.on_time_rate) * 100, 1) if row.on_time_rate is not None else None,
            "avg_review_score": round(float(review_row.avg_score), 2) if review_row.avg_score else None,
            "total_delivered_orders": int(row.total_delivered),
        },
    }


def get_delivery_by_state(db: Session) -> Dict[str, Any]:
    if not _has_delivered_orders(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    rows = (
        db.query(
            Customer.customer_state.label("state"),
            func.avg(
                func.extract(
                    "epoch",
                    Order.order_delivered_customer_date - Order.order_purchase_timestamp,
                )
                / 86400.0
            ).label("avg_delivery_days"),
            func.count(Order.order_id).label("order_count"),
        )
        .join(Customer, Order.customer_id == Customer.customer_id)
        .filter(
            Order.order_delivered_customer_date.isnot(None),
            Order.order_status == "delivered",
        )
        .group_by(Customer.customer_state)
        .order_by(func.avg(
            func.extract(
                "epoch",
                Order.order_delivered_customer_date - Order.order_purchase_timestamp,
            )
            / 86400.0
        ))
        .all()
    )

    data = [
        {
            "state": r.state,
            "avg_delivery_days": round(float(r.avg_delivery_days), 1) if r.avg_delivery_days else None,
            "order_count": int(r.order_count),
        }
        for r in rows
    ]
    return {"status": "ok", "message": "", "data": data}


def get_review_distribution(db: Session) -> Dict[str, Any]:
    if not _has_delivered_orders(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    rows = (
        db.query(
            OrderReview.review_score.label("review_score"),
            func.count(OrderReview.id).label("count"),
        )
        .join(Order, OrderReview.order_id == Order.order_id)
        .filter(
            Order.order_delivered_customer_date.isnot(None),
            Order.order_status == "delivered",
        )
        .group_by(OrderReview.review_score)
        .order_by(OrderReview.review_score)
        .all()
    )

    data = [{"review_score": int(r.review_score), "count": int(r.count)} for r in rows]
    return {"status": "ok", "message": "", "data": data}


def get_late_analysis(db: Session) -> Dict[str, Any]:
    if not _has_delivered_orders(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": {}}

    # On-time orders
    on_time_q = (
        db.query(
            func.count(Order.order_id).label("count"),
            func.avg(OrderReview.review_score).label("avg_review"),
        )
        .outerjoin(OrderReview, Order.order_id == OrderReview.order_id)
        .filter(
            Order.order_delivered_customer_date.isnot(None),
            Order.order_status == "delivered",
            Order.order_delivered_customer_date <= Order.order_estimated_delivery_date,
        )
        .one()
    )

    # Late orders
    late_q = (
        db.query(
            func.count(Order.order_id).label("count"),
            func.avg(OrderReview.review_score).label("avg_review"),
        )
        .outerjoin(OrderReview, Order.order_id == OrderReview.order_id)
        .filter(
            Order.order_delivered_customer_date.isnot(None),
            Order.order_status == "delivered",
            Order.order_delivered_customer_date > Order.order_estimated_delivery_date,
        )
        .one()
    )

    return {
        "status": "ok",
        "message": "",
        "data": {
            "on_time_count": int(on_time_q.count or 0),
            "late_count": int(late_q.count or 0),
            "on_time_avg_review": round(float(on_time_q.avg_review), 2) if on_time_q.avg_review else None,
            "late_avg_review": round(float(late_q.avg_review), 2) if late_q.avg_review else None,
        },
    }
