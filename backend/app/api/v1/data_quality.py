from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.data_quality import DataQualityReport
from app.services.data_quality_service import DataQualityService

router = APIRouter()


@router.get(
    "/data-quality",
    response_model=DataQualityReport,
    summary="Real Data Quality & Ingestion Status",
    description="Inspects real raw files in data/raw and queries PostgreSQL schema tables for row counts, completeness, and null rates.",
)
def get_data_quality(db: Session = Depends(get_db)) -> DataQualityReport:
    report = DataQualityService.generate_report(db)
    return report
