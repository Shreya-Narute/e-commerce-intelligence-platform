from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services import delivery_service

router = APIRouter()


@router.get(
    "/summary",
    summary="Delivery Summary",
    description="Average delivery days, on-time rate, and average review score for delivered orders.",
)
def delivery_summary(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return delivery_service.get_delivery_summary(db)


@router.get(
    "/by-state",
    summary="Delivery Performance by State",
    description="Average delivery days per customer state.",
)
def delivery_by_state(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return delivery_service.get_delivery_by_state(db)


@router.get(
    "/review-distribution",
    summary="Review Score Distribution",
    description="Count of reviews for each score (1-5) on delivered orders.",
)
def review_distribution(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return delivery_service.get_review_distribution(db)


@router.get(
    "/late-analysis",
    summary="Late vs On-Time Analysis",
    description="Count and average review score for late and on-time delivered orders.",
)
def late_analysis(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return delivery_service.get_late_analysis(db)
