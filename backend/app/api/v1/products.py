from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services import product_service

router = APIRouter()


@router.get(
    "/top-revenue",
    summary="Top Revenue Products",
    description="Top 20 products by total revenue (sum of payment_value).",
)
def top_revenue_products(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return product_service.get_top_revenue_products(db, limit=20)


@router.get(
    "/categories",
    summary="All Categories",
    description="All product categories with order count and total revenue.",
)
def categories(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return product_service.get_categories(db)


@router.get(
    "/category-trend",
    summary="Category Trend",
    description="Monthly order count for the top 5 categories by total orders.",
)
def category_trend(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return product_service.get_category_trend(db)


@router.get(
    "/dimensions",
    summary="Product Dimensions by Category",
    description="Average weight and physical dimensions per product category.",
)
def product_dimensions(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return product_service.get_product_dimensions(db)
