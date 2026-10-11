from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.analytics import rfm as rfm_analytics
from app.ml import forecasting as forecasting_ml

router = APIRouter()


@router.get(
    "/rfm",
    summary="RFM Model Evaluation",
    description="Silhouette score, cluster sizes, and segment distribution from the cached RFM model.",
)
def rfm_model_eval(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    result = rfm_analytics.compute_rfm(db)
    if result.get("status") != "ok":
        return {
            "status": result.get("status", "no_data"),
            "message": result.get("message", ""),
            "silhouette_score": None,
            "cluster_sizes": None,
            "segment_distribution": None,
        }

    segments = result.get("segments", [])
    segment_distribution = {s["segment"]: s["customer_count"] for s in segments}

    return {
        "status": "ok",
        "message": "",
        "silhouette_score": result.get("silhouette_score"),
        "cluster_sizes": result.get("cluster_sizes"),
        "segment_distribution": segment_distribution,
    }


@router.get(
    "/forecasting",
    summary="Forecasting Model Evaluation",
    description="MAE, RMSE, and MAPE from the cached revenue forecast model.",
)
def forecasting_model_eval(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    result = forecasting_ml.compute_revenue_forecast(db)
    if result.get("status") != "ok":
        return {
            "status": result.get("status", "no_data"),
            "message": result.get("message", ""),
            "mae": None,
            "rmse": None,
            "mape": None,
        }

    return {
        "status": "ok",
        "message": "",
        "mae": result.get("mae"),
        "rmse": result.get("rmse"),
        "mape": result.get("mape"),
    }
