from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.ml import forecasting as forecasting_ml

router = APIRouter()


@router.get(
    "/revenue",
    summary="Revenue Forecast",
    description="3-month revenue forecast using SimpleExpSmoothing with MAE/RMSE metrics.",
)
def revenue_forecast(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return forecasting_ml.compute_revenue_forecast(db)


@router.get(
    "/orders",
    summary="Order Count Forecast",
    description="3-month order count forecast using SimpleExpSmoothing with MAE/RMSE metrics.",
)
def orders_forecast(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    return forecasting_ml.compute_orders_forecast(db)
