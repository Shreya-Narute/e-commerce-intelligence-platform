from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services import customer_service

router = APIRouter()


@router.get(
    "/summary",
    summary="Customer Summary",
    description=(
        "Total unique customers, average orders per customer, "
        "and average spend per customer."
    ),
)
def customer_summary(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return customer_service.get_customer_summary(db)


@router.get(
    "/top-states",
    summary="Customers by State",
    description="Top 10 states by number of unique customers.",
)
def top_states(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return customer_service.get_top_states(db, limit=10)


@router.get(
    "/purchase-frequency",
    summary="Purchase Frequency Distribution",
    description=(
        "Distribution of orders per unique customer — shows how many "
        "customers ordered 1x, 2x, 3x+ etc."
    ),
)
def purchase_frequency(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return customer_service.get_purchase_frequency(db)


@router.get(
    "/cohort",
    summary="Monthly Customer Cohort",
    description=(
        "New customers per month where the cohort month is the first "
        "purchase month (MIN order_purchase_timestamp) per customer_unique_id."
    ),
)
def cohort(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return customer_service.get_cohort(db)
