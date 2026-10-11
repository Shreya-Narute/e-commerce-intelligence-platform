from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services import payment_service

router = APIRouter()


@router.get(
    "/summary",
    summary="Payment Summary",
    description="Total payment value, average installments, and breakdown by payment type.",
)
def payment_summary(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return payment_service.get_payment_summary(db)


@router.get(
    "/installment-distribution",
    summary="Installment Distribution",
    description="Transaction count grouped by installment count. 12+ installments are grouped together.",
)
def installment_distribution(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return payment_service.get_installment_distribution(db)


@router.get(
    "/monthly-volume",
    summary="Monthly Payment Volume",
    description="Monthly total payment value and transaction count.",
)
def monthly_volume(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return payment_service.get_monthly_volume(db)
