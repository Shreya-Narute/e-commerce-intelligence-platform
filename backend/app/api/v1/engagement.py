from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services import engagement_service

router = APIRouter()


@router.get(
    "/risk-summary",
    summary="Customer Engagement Risk Summary",
    description=(
        "Rule-based engagement risk tiers (Active / Cooling / At Risk / Inactive) "
        "based on days since last purchase. NOT an ML churn prediction."
    ),
)
def risk_summary(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return engagement_service.get_risk_summary(db)


@router.get(
    "/at-risk-customers",
    summary="At Risk & Inactive Customers",
    description="Paginated list of customers classified as At Risk or Inactive.",
)
def at_risk_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return engagement_service.get_at_risk_customers(db, page=page, page_size=page_size)
