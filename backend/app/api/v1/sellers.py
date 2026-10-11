from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services import seller_service

router = APIRouter()


@router.get(
    "/summary",
    summary="Seller Summary",
    description="Total sellers and average revenue per seller.",
)
def seller_summary(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return seller_service.get_seller_summary(db)


@router.get(
    "/top-revenue",
    summary="Top Revenue Sellers",
    description="Top 20 sellers by total revenue.",
)
def top_revenue_sellers(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return seller_service.get_top_revenue_sellers(db, limit=20)


@router.get(
    "/by-state",
    summary="Sellers by State",
    description="Seller count and total revenue grouped by state.",
)
def sellers_by_state(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return seller_service.get_sellers_by_state(db)


@router.get(
    "/performance",
    summary="Seller Performance",
    description="Top 100 sellers by avg review score with avg delivery days.",
)
def seller_performance(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return seller_service.get_seller_performance(db)
