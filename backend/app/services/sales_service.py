"""
Sales Analytics Service
=======================
Revenue definition: sum of order_payments.payment_value for orders joined to
order_payments.  A single order may have multiple payment rows (split payments),
so payment_value is summed at the order level before aggregating across orders.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import func, distinct, cast, String
from sqlalchemy.orm import Session

from app.models.olist import Order, OrderPayment, Customer, ProductCategoryTranslation, Product, OrderItem

_NO_DATA_MSG = "Dataset not loaded. Please ingest the Olist CSV data first."


def _has_orders(db: Session) -> bool:
    return db.query(func.count(Order.order_id)).scalar() > 0


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def get_sales_summary(db: Session) -> Dict[str, Any]:
    if not _has_orders(db):
        return {
            "status": "no_data",
            "message": _NO_DATA_MSG,
            "data": {
                "total_revenue": None,
                "total_orders": 0,
                "average_order_value": None,
                "date_range_start": None,
                "date_range_end": None,
                "status": "no_data",
            },
        }

    # Revenue per order (sum payment_value grouped by order_id)
    order_revenue = (
        db.query(
            OrderPayment.order_id,
            func.sum(OrderPayment.payment_value).label("order_revenue"),
        )
        .group_by(OrderPayment.order_id)
        .subquery()
    )

    row = db.query(
        func.sum(order_revenue.c.order_revenue).label("total_revenue"),
        func.count(order_revenue.c.order_id).label("total_orders"),
    ).one()

    date_row = db.query(
        func.min(Order.order_purchase_timestamp).label("min_date"),
        func.max(Order.order_purchase_timestamp).label("max_date"),
    ).one()

    total_revenue = float(row.total_revenue) if row.total_revenue else 0.0
    total_orders = int(row.total_orders) if row.total_orders else 0
    aov = round(total_revenue / total_orders, 2) if total_orders > 0 else None

    return {
        "status": "ok",
        "message": "",
        "data": {
            "total_revenue": round(total_revenue, 2),
            "total_orders": total_orders,
            "average_order_value": aov,
            "date_range_start": date_row.min_date.isoformat() if date_row.min_date else None,
            "date_range_end": date_row.max_date.isoformat() if date_row.max_date else None,
            "status": "ok",
        },
    }


# ---------------------------------------------------------------------------
# Monthly revenue
# ---------------------------------------------------------------------------

def get_monthly_revenue(db: Session) -> Dict[str, Any]:
    if not _has_orders(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    rows = (
        db.query(
            func.to_char(Order.order_purchase_timestamp, "YYYY-MM").label("year_month"),
            func.sum(OrderPayment.payment_value).label("revenue"),
            func.count(distinct(Order.order_id)).label("order_count"),
        )
        .join(OrderPayment, Order.order_id == OrderPayment.order_id)
        .group_by(func.to_char(Order.order_purchase_timestamp, "YYYY-MM"))
        .order_by(func.to_char(Order.order_purchase_timestamp, "YYYY-MM"))
        .all()
    )

    data = [
        {"year_month": r.year_month, "revenue": round(float(r.revenue), 2), "order_count": int(r.order_count)}
        for r in rows
    ]
    return {"status": "ok", "message": "", "data": data}


# ---------------------------------------------------------------------------
# Revenue by state
# ---------------------------------------------------------------------------

def get_revenue_by_state(db: Session, limit: int = 10) -> Dict[str, Any]:
    if not _has_orders(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    rows = (
        db.query(
            Customer.customer_state.label("state"),
            func.sum(OrderPayment.payment_value).label("revenue"),
            func.count(distinct(Order.order_id)).label("order_count"),
        )
        .join(Order, Customer.customer_id == Order.customer_id)
        .join(OrderPayment, Order.order_id == OrderPayment.order_id)
        .group_by(Customer.customer_state)
        .order_by(func.sum(OrderPayment.payment_value).desc())
        .limit(limit)
        .all()
    )

    data = [
        {"state": r.state, "revenue": round(float(r.revenue), 2), "order_count": int(r.order_count)}
        for r in rows
    ]
    return {"status": "ok", "message": "", "data": data}


# ---------------------------------------------------------------------------
# Revenue by category
# ---------------------------------------------------------------------------

def get_revenue_by_category(db: Session, limit: int = 15) -> Dict[str, Any]:
    if not _has_orders(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    rows = (
        db.query(
            func.coalesce(
                ProductCategoryTranslation.product_category_name_english,
                Product.product_category_name,
                "unknown",
            ).label("category_name"),
            func.sum(OrderPayment.payment_value).label("revenue"),
            func.count(distinct(Order.order_id)).label("order_count"),
        )
        .join(OrderItem, Order.order_id == OrderItem.order_id)
        .join(Product, OrderItem.product_id == Product.product_id)
        .outerjoin(
            ProductCategoryTranslation,
            Product.product_category_name == ProductCategoryTranslation.product_category_name,
        )
        .join(OrderPayment, Order.order_id == OrderPayment.order_id)
        .group_by(
            func.coalesce(
                ProductCategoryTranslation.product_category_name_english,
                Product.product_category_name,
                "unknown",
            )
        )
        .order_by(func.sum(OrderPayment.payment_value).desc())
        .limit(limit)
        .all()
    )

    data = [
        {"category_name": r.category_name, "revenue": round(float(r.revenue), 2), "order_count": int(r.order_count)}
        for r in rows
    ]
    return {"status": "ok", "message": "", "data": data}


# ---------------------------------------------------------------------------
# Order status counts
# ---------------------------------------------------------------------------

def get_order_status_counts(db: Session) -> Dict[str, Any]:
    if not _has_orders(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    rows = (
        db.query(
            Order.order_status.label("status"),
            func.count(Order.order_id).label("count"),
        )
        .group_by(Order.order_status)
        .order_by(func.count(Order.order_id).desc())
        .all()
    )

    data = [{"status": r.status, "count": int(r.count)} for r in rows]
    return {"status": "ok", "message": "", "data": data}


# ---------------------------------------------------------------------------
# Payment type revenue
# ---------------------------------------------------------------------------

def get_payment_type_revenue(db: Session) -> Dict[str, Any]:
    if not _has_orders(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    rows = (
        db.query(
            OrderPayment.payment_type.label("payment_type"),
            func.sum(OrderPayment.payment_value).label("revenue"),
            func.count(OrderPayment.payment_sequential).label("transaction_count"),
        )
        .group_by(OrderPayment.payment_type)
        .order_by(func.sum(OrderPayment.payment_value).desc())
        .all()
    )

    data = [
        {
            "payment_type": r.payment_type,
            "revenue": round(float(r.revenue), 2),
            "transaction_count": int(r.transaction_count),
        }
        for r in rows
    ]
    return {"status": "ok", "message": "", "data": data}
