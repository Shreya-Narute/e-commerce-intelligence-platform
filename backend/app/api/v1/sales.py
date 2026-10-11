from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services import sales_service

router = APIRouter()


@router.get(
    "/summary",
    summary="Sales Summary",
    description=(
        "Returns total revenue (sum of order_payments.payment_value), "
        "total orders, average order value, and date range."
    ),
)
def sales_summary(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return sales_service.get_sales_summary(db)


@router.get(
    "/monthly",
    summary="Monthly Revenue",
    description="Revenue and order count grouped by calendar month (YYYY-MM).",
)
def monthly_revenue(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return sales_service.get_monthly_revenue(db)


@router.get(
    "/by-state",
    summary="Revenue by State",
    description="Top 10 states by total revenue (sum of payment_value).",
)
def revenue_by_state(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return sales_service.get_revenue_by_state(db, limit=10)


@router.get(
    "/by-category",
    summary="Revenue by Category",
    description="Top 15 product categories by total revenue.",
)
def revenue_by_category(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return sales_service.get_revenue_by_category(db, limit=15)


@router.get(
    "/order-status",
    summary="Order Status Counts",
    description="Count of orders grouped by order_status.",
)
def order_status(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return sales_service.get_order_status_counts(db)


@router.get(
    "/payment-types",
    summary="Revenue by Payment Type",
    description="Total revenue and transaction count grouped by payment_type.",
)
def payment_types(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return sales_service.get_payment_type_revenue(db)
