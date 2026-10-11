from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services import insights_service

router = APIRouter()


@router.get(
    "/summary",
    summary="Business Insights Summary",
    description="8-12 business insights computed from real data with titles, values, context, and recommendations.",
)
def insights_summary(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return insights_service.get_insights_summary(db)
