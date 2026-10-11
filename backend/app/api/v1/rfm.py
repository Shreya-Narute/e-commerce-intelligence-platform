from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.analytics import rfm as rfm_analytics

router = APIRouter()


@router.get(
    "/segments",
    summary="RFM Segments",
    description="RFM customer segments with counts and average R/F/M values.",
)
def rfm_segments(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    result = rfm_analytics.compute_rfm(db)
    if result.get("status") != "ok":
        return result
    return {
        "status": "ok",
        "message": "",
        "reference_date": result.get("reference_date"),
        "total_customers": result.get("total_customers"),
        "silhouette_score": result.get("silhouette_score"),
        "data": result.get("segments", []),
    }


@router.get(
    "/distribution",
    summary="RFM Score Distribution",
    description="Count of customers at each R, F, M score level (1-5).",
)
def rfm_distribution(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    result = rfm_analytics.compute_rfm(db)
    if result.get("status") != "ok":
        return result
    return {
        "status": "ok",
        "message": "",
        "data": result.get("score_distribution", []),
    }


@router.get(
    "/customers",
    summary="RFM Customer List",
    description="Paginated list of customers with their R/F/M scores and segments.",
)
def rfm_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    result = rfm_analytics.compute_rfm(db)
    if result.get("status") != "ok":
        return result

    customers = result.get("customers", [])
    total = len(customers)
    offset = (page - 1) * page_size
    page_data = customers[offset : offset + page_size]

    return {
        "status": "ok",
        "message": "",
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": page_data,
    }
