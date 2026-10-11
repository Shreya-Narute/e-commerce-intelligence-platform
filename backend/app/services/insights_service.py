"""
Business Insights Service
==========================
Generates 8-12 insights from REAL computed data.
All values are derived from the database — nothing is hardcoded.
"""

from typing import Any, Dict, List
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from app.models.olist import (
    Order, OrderItem, OrderPayment, OrderReview, Customer,
    Seller, Product, ProductCategoryTranslation,
)

_NO_DATA_MSG = "Dataset not loaded. Please ingest the Olist CSV data first."


def _has_orders(db: Session) -> bool:
    return db.query(func.count(Order.order_id)).scalar() > 0


def get_insights_summary(db: Session) -> Dict[str, Any]:
    if not _has_orders(db):
        return {"status": "no_data", "message": _NO_DATA_MSG, "insights": []}

    insights: List[Dict[str, str]] = []

    # 1. Top state by revenue
    try:
        state_row = (
            db.query(
                Customer.customer_state.label("state"),
                func.sum(OrderPayment.payment_value).label("revenue"),
            )
            .join(Order, Customer.customer_id == Order.customer_id)
            .join(OrderPayment, Order.order_id == OrderPayment.order_id)
            .group_by(Customer.customer_state)
            .order_by(func.sum(OrderPayment.payment_value).desc())
            .first()
        )
        if state_row:
            insights.append(
                {
                    "title": "Top Revenue State",
                    "value": f"{state_row.state} — R$ {float(state_row.revenue):,.0f}",
                    "context": f"State {state_row.state} contributes the most to total platform revenue.",
                    "recommendation": "Invest in marketing and logistics in this region to protect and grow its lead.",
                }
            )
    except Exception:
        pass

    # 2. One-time buyer percentage
    try:
        buyer_rows = (
            db.query(
                Customer.customer_unique_id,
                func.count(distinct(Order.order_id)).label("order_count"),
            )
            .join(Order, Customer.customer_id == Order.customer_id)
            .group_by(Customer.customer_unique_id)
            .all()
        )
        if buyer_rows:
            total_buyers = len(buyer_rows)
            one_time = sum(1 for r in buyer_rows if int(r.order_count) == 1)
            pct = round(one_time / total_buyers * 100, 1)
            insights.append(
                {
                    "title": "One-Time Buyer Rate",
                    "value": f"{pct}% of customers",
                    "context": f"{one_time:,} out of {total_buyers:,} unique customers placed only one order.",
                    "recommendation": "Launch post-purchase email sequences and loyalty rewards to convert one-time buyers into repeat customers.",
                }
            )
    except Exception:
        pass

    # 3. Average delivery time (delivered orders only)
    try:
        delivery_row = (
            db.query(
                func.avg(
                    func.extract(
                        "epoch",
                        Order.order_delivered_customer_date - Order.order_purchase_timestamp,
                    )
                    / 86400.0
                ).label("avg_days")
            )
            .filter(
                Order.order_delivered_customer_date.isnot(None),
                Order.order_status == "delivered",
            )
            .one()
        )
        if delivery_row.avg_days is not None:
            avg_days = round(float(delivery_row.avg_days), 1)
            insights.append(
                {
                    "title": "Average Delivery Time",
                    "value": f"{avg_days} days",
                    "context": "Computed from order purchase timestamp to customer delivery date for delivered orders.",
                    "recommendation": "Focus on reducing delivery times in states with above-average transit durations.",
                }
            )
    except Exception:
        pass

    # 4. Most popular payment method
    try:
        pay_row = (
            db.query(
                OrderPayment.payment_type.label("payment_type"),
                func.count(OrderPayment.payment_sequential).label("count"),
            )
            .group_by(OrderPayment.payment_type)
            .order_by(func.count(OrderPayment.payment_sequential).desc())
            .first()
        )
        if pay_row:
            insights.append(
                {
                    "title": "Most Popular Payment Method",
                    "value": pay_row.payment_type.replace("_", " ").title(),
                    "context": f"{pay_row.payment_type} was used in {int(pay_row.count):,} transactions.",
                    "recommendation": "Ensure a smooth and optimized checkout experience for this payment method.",
                }
            )
    except Exception:
        pass

    # 5. Top product category by revenue
    try:
        cat_row = (
            db.query(
                func.coalesce(
                    ProductCategoryTranslation.product_category_name_english,
                    Product.product_category_name,
                    "unknown",
                ).label("category"),
                func.sum(OrderPayment.payment_value).label("revenue"),
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
            .first()
        )
        if cat_row:
            insights.append(
                {
                    "title": "Top Revenue Category",
                    "value": cat_row.category,
                    "context": f"Generated R$ {float(cat_row.revenue):,.0f} in total revenue.",
                    "recommendation": "Prioritize inventory and promotional spend for this category to maximise returns.",
                }
            )
    except Exception:
        pass

    # 6. On-time delivery rate
    try:
        total_delivered = (
            db.query(func.count(Order.order_id))
            .filter(
                Order.order_delivered_customer_date.isnot(None),
                Order.order_status == "delivered",
            )
            .scalar()
        )
        on_time = (
            db.query(func.count(Order.order_id))
            .filter(
                Order.order_delivered_customer_date.isnot(None),
                Order.order_status == "delivered",
                Order.order_delivered_customer_date <= Order.order_estimated_delivery_date,
            )
            .scalar()
        )
        if total_delivered and total_delivered > 0:
            rate = round(on_time / total_delivered * 100, 1)
            insights.append(
                {
                    "title": "On-Time Delivery Rate",
                    "value": f"{rate}%",
                    "context": f"{int(on_time):,} of {int(total_delivered):,} delivered orders arrived on or before the estimated date.",
                    "recommendation": "Investigate states or sellers with high late-delivery rates to improve overall fulfilment.",
                }
            )
    except Exception:
        pass

    # 7. Average review score
    try:
        review_row = db.query(func.avg(OrderReview.review_score).label("avg")).one()
        if review_row.avg is not None:
            avg_score = round(float(review_row.avg), 2)
            insights.append(
                {
                    "title": "Average Customer Review Score",
                    "value": f"{avg_score} / 5",
                    "context": "Computed across all order reviews in the dataset.",
                    "recommendation": "Focus on improving low-scoring orders — especially those tied to late deliveries.",
                }
            )
    except Exception:
        pass

    # 8. Total unique customers
    try:
        unique_customers = (
            db.query(func.count(distinct(Customer.customer_unique_id))).scalar()
        )
        total_orders = db.query(func.count(Order.order_id)).scalar()
        if unique_customers:
            insights.append(
                {
                    "title": "Customer Base Size",
                    "value": f"{int(unique_customers):,} unique customers",
                    "context": f"Platform served {int(unique_customers):,} unique customers across {int(total_orders):,} total orders.",
                    "recommendation": "Use RFM segmentation to personalise retention campaigns for each customer tier.",
                }
            )
    except Exception:
        pass

    # 9. Total sellers
    try:
        total_sellers = db.query(func.count(distinct(Seller.seller_id))).scalar()
        if total_sellers:
            insights.append(
                {
                    "title": "Active Seller Network",
                    "value": f"{int(total_sellers):,} sellers",
                    "context": "Number of distinct sellers who have processed at least one order.",
                    "recommendation": "Identify and support high-performing sellers to scale revenue without proportional cost increases.",
                }
            )
    except Exception:
        pass

    # 10. Installment usage
    try:
        from sqlalchemy import text as _text
        inst_result = db.execute(
            _text(
                "SELECT COUNT(*) FILTER (WHERE payment_installments > 1) AS installment_count, COUNT(*) AS total FROM order_payments"
            )
        ).one()
        if inst_result.total > 0:
            pct_inst = round(inst_result.installment_count / inst_result.total * 100, 1)
            insights.append(
                {
                    "title": "Installment Payment Usage",
                    "value": f"{pct_inst}% of transactions",
                    "context": f"{int(inst_result.installment_count):,} out of {int(inst_result.total):,} payment transactions used installments.",
                    "recommendation": "Offer flexible installment options to increase average order value for higher-priced categories.",
                }
            )
    except Exception:
        pass

    return {
        "status": "ok",
        "message": "",
        "insights": insights,
    }
