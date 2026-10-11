"""
Seller Analytics Service
=========================
Provides seller-level revenue, state breakdown, and performance metrics.
"""

from typing import Any, Dict, List
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from app.models.olist import Order, OrderItem, OrderPayment, OrderReview, Seller, Customer

_NO_DATA_MSG = "Dataset not loaded. Please ingest the Olist CSV data first."


def _has_sellers(db: Session) -> bool:
    return db.query(func.count(Seller.seller_id)).scalar() > 0


def get_seller_summary(db: Session) -> Dict[str, Any]:
    if not _has_sellers(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": {}}

    total_sellers = db.query(func.count(Seller.seller_id)).scalar()

    revenue_row = (
        db.query(
            func.sum(OrderPayment.payment_value).label("total_revenue"),
            func.count(distinct(OrderItem.seller_id)).label("sellers_with_orders"),
        )
        .join(OrderItem, OrderPayment.order_id == OrderItem.order_id)
        .one()
    )

    total_revenue = float(revenue_row.total_revenue or 0)
    sellers_with_orders = int(revenue_row.sellers_with_orders or 0)
    avg_revenue = round(total_revenue / sellers_with_orders, 2) if sellers_with_orders > 0 else None

    return {
        "status": "ok",
        "message": "",
        "data": {
            "total_sellers": int(total_sellers),
            "avg_revenue_per_seller": avg_revenue,
        },
    }


def get_top_revenue_sellers(db: Session, limit: int = 20) -> Dict[str, Any]:
    if not _has_sellers(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    rows = (
        db.query(
            OrderItem.seller_id.label("seller_id"),
            Seller.seller_state.label("seller_state"),
            func.sum(OrderPayment.payment_value).label("total_revenue"),
            func.count(distinct(OrderItem.order_id)).label("order_count"),
        )
        .join(Seller, OrderItem.seller_id == Seller.seller_id)
        .join(OrderPayment, OrderItem.order_id == OrderPayment.order_id)
        .group_by(OrderItem.seller_id, Seller.seller_state)
        .order_by(func.sum(OrderPayment.payment_value).desc())
        .limit(limit)
        .all()
    )

    data = [
        {
            "seller_id": r.seller_id,
            "seller_state": r.seller_state,
            "total_revenue": round(float(r.total_revenue), 2),
            "order_count": int(r.order_count),
        }
        for r in rows
    ]
    return {"status": "ok", "message": "", "data": data}


def get_sellers_by_state(db: Session) -> Dict[str, Any]:
    if not _has_sellers(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    rows = (
        db.query(
            Seller.seller_state.label("state"),
            func.count(distinct(Seller.seller_id)).label("seller_count"),
            func.coalesce(func.sum(OrderPayment.payment_value), 0).label("total_revenue"),
        )
        .outerjoin(OrderItem, Seller.seller_id == OrderItem.seller_id)
        .outerjoin(OrderPayment, OrderItem.order_id == OrderPayment.order_id)
        .group_by(Seller.seller_state)
        .order_by(func.count(distinct(Seller.seller_id)).desc())
        .all()
    )

    data = [
        {
            "state": r.state,
            "seller_count": int(r.seller_count),
            "total_revenue": round(float(r.total_revenue), 2),
        }
        for r in rows
    ]
    return {"status": "ok", "message": "", "data": data}


def get_seller_performance(db: Session) -> Dict[str, Any]:
    if not _has_sellers(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    rows = (
        db.query(
            OrderItem.seller_id.label("seller_id"),
            Seller.seller_state.label("seller_state"),
            func.avg(OrderReview.review_score).label("avg_review_score"),
            func.avg(
                func.extract(
                    "epoch",
                    Order.order_delivered_customer_date - Order.order_purchase_timestamp,
                )
                / 86400.0
            ).label("avg_delivery_days"),
            func.count(distinct(OrderItem.order_id)).label("order_count"),
        )
        .join(Seller, OrderItem.seller_id == Seller.seller_id)
        .join(Order, OrderItem.order_id == Order.order_id)
        .outerjoin(OrderReview, Order.order_id == OrderReview.order_id)
        .filter(
            Order.order_delivered_customer_date.isnot(None),
            Order.order_status == "delivered",
        )
        .group_by(OrderItem.seller_id, Seller.seller_state)
        .order_by(func.avg(OrderReview.review_score).desc().nullslast())
        .limit(100)
        .all()
    )

    data = [
        {
            "seller_id": r.seller_id,
            "seller_state": r.seller_state,
            "avg_review_score": round(float(r.avg_review_score), 2) if r.avg_review_score is not None else None,
            "avg_delivery_days": round(float(r.avg_delivery_days), 1) if r.avg_delivery_days is not None else None,
            "order_count": int(r.order_count),
        }
        for r in rows
    ]
    return {"status": "ok", "message": "", "data": data}
