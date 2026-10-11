
"""
Product Analytics Service
=========================
All revenue figures use sum of order_payments.payment_value joined to orders.
"""

from typing import Dict, Any

from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from app.models.olist import (
    Order,
    OrderPayment,
    OrderItem,
    Product,
    ProductCategoryTranslation,
)

_NO_DATA_MSG = "Dataset not loaded. Please ingest the Olist CSV data first."


def _has_products(db: Session) -> bool:
    return db.query(func.count(Product.product_id)).scalar() > 0


def _has_orders(db: Session) -> bool:
    return db.query(func.count(Order.order_id)).scalar() > 0


# ---------------------------------------------------------------------------
# Top revenue products
# ---------------------------------------------------------------------------

def get_top_revenue_products(
    db: Session, limit: int = 20
) -> Dict[str, Any]:
    if not _has_orders(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    rows = (
        db.query(
            Product.product_id,
            func.coalesce(
                ProductCategoryTranslation.product_category_name_english,
                Product.product_category_name,
                "unknown",
            ).label("category_name"),
            func.sum(OrderPayment.payment_value).label("revenue"),
            func.count(distinct(Order.order_id)).label("order_count"),
        )
        .select_from(Product)
        .join(OrderItem, Product.product_id == OrderItem.product_id)
        .join(Order, OrderItem.order_id == Order.order_id)
        .join(OrderPayment, Order.order_id == OrderPayment.order_id)
        .outerjoin(
            ProductCategoryTranslation,
            Product.product_category_name
            == ProductCategoryTranslation.product_category_name,
        )
        .group_by(
            Product.product_id,
            func.coalesce(
                ProductCategoryTranslation.product_category_name_english,
                Product.product_category_name,
                "unknown",
            ),
        )
        .order_by(func.sum(OrderPayment.payment_value).desc())
        .limit(limit)
        .all()
    )

    data = [
        {
            "product_id": r.product_id,
            "category_name": r.category_name,
            "revenue": round(float(r.revenue), 2) if r.revenue else 0.0,
            "order_count": int(r.order_count) if r.order_count else 0,
        }
        for r in rows
    ]

    return {"status": "ok", "message": "", "data": data}


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

def get_categories(db: Session) -> Dict[str, Any]:
    if not _has_products(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    rows = (
        db.query(
            func.coalesce(
                ProductCategoryTranslation.product_category_name_english,
                Product.product_category_name,
                "unknown",
            ).label("category_name"),
            func.count(distinct(OrderItem.order_id)).label("order_count"),
            func.sum(OrderPayment.payment_value).label("revenue"),
        )
        .select_from(Product)
        .outerjoin(
            OrderItem,
            Product.product_id == OrderItem.product_id,
        )
        .outerjoin(
            Order,
            OrderItem.order_id == Order.order_id,
        )
        .outerjoin(
            OrderPayment,
            Order.order_id == OrderPayment.order_id,
        )
        .outerjoin(
            ProductCategoryTranslation,
            Product.product_category_name
            == ProductCategoryTranslation.product_category_name,
        )
        .group_by(
            func.coalesce(
                ProductCategoryTranslation.product_category_name_english,
                Product.product_category_name,
                "unknown",
            )
        )
        .order_by(func.sum(OrderPayment.payment_value).desc())
        .all()
    )

    data = [
        {
            "category_name": r.category_name,
            "order_count": int(r.order_count) if r.order_count else 0,
            "revenue": round(float(r.revenue), 2) if r.revenue else 0.0,
        }
        for r in rows
    ]

    return {"status": "ok", "message": "", "data": data}


# ---------------------------------------------------------------------------
# Category trend (monthly order counts for top 5 categories by total orders)
# ---------------------------------------------------------------------------

def get_category_trend(db: Session) -> Dict[str, Any]:
    if not _has_orders(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    top5_subq = (
        db.query(
            func.coalesce(
                ProductCategoryTranslation.product_category_name_english,
                Product.product_category_name,
                "unknown",
            ).label("category_name"),
            func.count(distinct(Order.order_id)).label("total_orders"),
        )
        .select_from(Product)
        .join(OrderItem, Product.product_id == OrderItem.product_id)
        .join(Order, OrderItem.order_id == Order.order_id)
        .outerjoin(
            ProductCategoryTranslation,
            Product.product_category_name
            == ProductCategoryTranslation.product_category_name,
        )
        .group_by(
            func.coalesce(
                ProductCategoryTranslation.product_category_name_english,
                Product.product_category_name,
                "unknown",
            )
        )
        .order_by(func.count(distinct(Order.order_id)).desc())
        .limit(5)
        .subquery()
    )

    top5_names = [r[0] for r in db.query(top5_subq.c.category_name).all()]

    if not top5_names:
        return {"status": "ok", "message": "", "data": []}

    rows = (
        db.query(
            func.to_char(
                Order.order_purchase_timestamp, "YYYY-MM"
            ).label("year_month"),
            func.coalesce(
                ProductCategoryTranslation.product_category_name_english,
                Product.product_category_name,
                "unknown",
            ).label("category_name"),
            func.count(distinct(Order.order_id)).label("order_count"),
        )
        .select_from(Order)
        .join(OrderItem, Order.order_id == OrderItem.order_id)
        .join(Product, OrderItem.product_id == Product.product_id)
        .outerjoin(
            ProductCategoryTranslation,
            Product.product_category_name
            == ProductCategoryTranslation.product_category_name,
        )
        .filter(
            func.coalesce(
                ProductCategoryTranslation.product_category_name_english,
                Product.product_category_name,
                "unknown",
            ).in_(top5_names)
        )
        .group_by(
            func.to_char(
                Order.order_purchase_timestamp, "YYYY-MM"
            ),
            func.coalesce(
                ProductCategoryTranslation.product_category_name_english,
                Product.product_category_name,
                "unknown",
            ),
        )
        .order_by(
            func.to_char(Order.order_purchase_timestamp, "YYYY-MM")
        )
        .all()
    )

    data = [
        {
            "year_month": r.year_month,
            "category_name": r.category_name,
            "order_count": int(r.order_count),
        }
        for r in rows
    ]

    return {"status": "ok", "message": "", "data": data}


# ---------------------------------------------------------------------------
# Product dimensions by category
# ---------------------------------------------------------------------------

def get_product_dimensions(db: Session) -> Dict[str, Any]:
    if not _has_products(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "data": []}

    rows = (
        db.query(
            func.coalesce(
                ProductCategoryTranslation.product_category_name_english,
                Product.product_category_name,
                "unknown",
            ).label("category_name"),
            func.avg(Product.product_weight_g).label("avg_weight_g"),
            func.avg(Product.product_length_cm).label("avg_length_cm"),
            func.avg(Product.product_height_cm).label("avg_height_cm"),
            func.avg(Product.product_width_cm).label("avg_width_cm"),
        )
        .select_from(Product)
        .outerjoin(
            ProductCategoryTranslation,
            Product.product_category_name
            == ProductCategoryTranslation.product_category_name,
        )
        .group_by(
            func.coalesce(
                ProductCategoryTranslation.product_category_name_english,
                Product.product_category_name,
                "unknown",
            )
        )
        .order_by(
            func.coalesce(
                ProductCategoryTranslation.product_category_name_english,
                Product.product_category_name,
                "unknown",
            )
        )
        .all()
    )

    def _round(value):
        return round(float(value), 2) if value is not None else None

    data = [
        {
            "category_name": r.category_name,
            "avg_weight_g": _round(r.avg_weight_g),
            "avg_length_cm": _round(r.avg_length_cm),
            "avg_height_cm": _round(r.avg_height_cm),
            "avg_width_cm": _round(r.avg_width_cm),
        }
        for r in rows
    ]

    return {"status": "ok", "message": "", "data": data}
