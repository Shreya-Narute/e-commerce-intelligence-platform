"""
Customer Analytics Service
==========================
Revenue definition: sum of order_payments.payment_value joined to orders.
Cohort: first purchase month defined as MIN(order_purchase_timestamp) per
customer_unique_id.
"""

from typing import Dict, Any
from sqlalchemy import func, distinct, cast, Integer
from sqlalchemy.orm import Session

from app.models.olist import Customer, Order, OrderPayment

_NO_DATA_MSG = "Dataset not loaded. Please ingest the Olist CSV data first."


def _has_customers(db: Session) -> bool:
    return db.query(func.count(Customer.customer_id)).scalar() > 0


def _has_orders(db: Session) -> bool:
    return db.query(func.count(Order.order_id)).scalar() > 0


# ---------------------------------------------------------------------------
# Customer summary
# ---------------------------------------------------------------------------

def get_customer_summary(db: Session) -> Dict[str, Any]:
    if not _has_customers(db):
        return {
            "status": "no_data",
            "message": _NO_DATA_MSG,
            "data": {
                "total_unique_customers": 0,
                "avg_orders_per_customer": None,
                "avg_spend_per_customer": None,
                "status": "no_data",
            },
        }

    total_unique = (
        db.query(func.count(distinct(Customer.customer_unique_id))).scalar() or 0
    )

    # Orders per unique customer
    orders_per_cust = (
        db.query(
            Customer.customer_unique_id,
            func.count(Order.order_id).label("n_orders"),
            func.sum(OrderPayment.payment_value).label("total_spend"),
        )
        .join(Order, Customer.customer_id == Order.customer_id)
        .join(OrderPayment, Order.order_id == OrderPayment.order_id)
        .group_by(Customer.customer_unique_id)
        .subquery()
    )

    agg = db.query(
        func.avg(orders_per_cust.c.n_orders).label("avg_orders"),
        func.avg(orders_per_cust.c.total_spend).label("avg_spend"),
    ).one()

    return {
        "status": "ok",
        "message": "",
        "data": {
            "total_unique_customers": int(total_unique),
            "avg_orders_per_customer": round(float(agg.avg_orders), 2) if agg.avg_orders else None,
            "avg_spend_per_customer": round(float(agg.avg_spend), 2) if agg.avg_spend else None,
            "status": "ok",
        },
    }


# ---------------------------------------------------------------------------
# Top states by unique customers
# ---------------------------------------------------------------------------

def get_top_states(db: Session, limit: int = 10) -> Dict[str, Any]:
    if not _has_customers(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    rows = (
        db.query(
            Customer.customer_state.label("state"),
            func.count(distinct(Customer.customer_unique_id)).label("unique_customers"),
        )
        .group_by(Customer.customer_state)
        .order_by(func.count(distinct(Customer.customer_unique_id)).desc())
        .limit(limit)
        .all()
    )

    data = [{"state": r.state, "unique_customers": int(r.unique_customers)} for r in rows]
    return {"status": "ok", "message": "", "data": data}


# ---------------------------------------------------------------------------
# Purchase frequency distribution
# ---------------------------------------------------------------------------

def get_purchase_frequency(db: Session) -> Dict[str, Any]:
    if not _has_orders(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    # Step 1: count orders per unique customer
    orders_per_cust = (
        db.query(
            Customer.customer_unique_id,
            func.count(Order.order_id).label("order_count"),
        )
        .join(Order, Customer.customer_id == Order.customer_id)
        .group_by(Customer.customer_unique_id)
        .subquery()
    )

    # Step 2: group customers by their order count
    rows = (
        db.query(
            orders_per_cust.c.order_count.label("order_count"),
            func.count(orders_per_cust.c.customer_unique_id).label("customer_count"),
        )
        .group_by(orders_per_cust.c.order_count)
        .order_by(orders_per_cust.c.order_count)
        .all()
    )

    data = [
        {"order_count": int(r.order_count), "customer_count": int(r.customer_count)}
        for r in rows
    ]
    return {"status": "ok", "message": "", "data": data}


# ---------------------------------------------------------------------------
# Monthly cohort — new customers (first purchase month)
# ---------------------------------------------------------------------------

def get_cohort(db: Session) -> Dict[str, Any]:
    if not _has_orders(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    # First purchase timestamp per unique customer
    first_purchase = (
        db.query(
            Customer.customer_unique_id,
            func.min(Order.order_purchase_timestamp).label("first_purchase"),
        )
        .join(Order, Customer.customer_id == Order.customer_id)
        .group_by(Customer.customer_unique_id)
        .subquery()
    )

    rows = (
        db.query(
            func.to_char(first_purchase.c.first_purchase, "YYYY-MM").label("cohort_month"),
            func.count(first_purchase.c.customer_unique_id).label("new_customers"),
        )
        .group_by(func.to_char(first_purchase.c.first_purchase, "YYYY-MM"))
        .order_by(func.to_char(first_purchase.c.first_purchase, "YYYY-MM"))
        .all()
    )

    data = [
        {"cohort_month": r.cohort_month, "new_customers": int(r.new_customers)}
        for r in rows
    ]
    return {"status": "ok", "message": "", "data": data}
