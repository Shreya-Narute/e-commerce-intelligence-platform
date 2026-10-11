import sys
from datetime import datetime, timezone
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.session import check_db_connection
from app.schemas.health import HealthResponse, DatabaseHealth, SystemInfo

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Platform Health & Connectivity Check",
    description="Validates running service state, environment metadata, and database heartbeat.",
)
def get_health() -> HealthResponse:
    db_connected, latency_ms, db_message = check_db_connection()

    overall_status = "healthy" if db_connected else "degraded"
    status_code = status.HTTP_200_OK if db_connected else status.HTTP_503_SERVICE_UNAVAILABLE

    payload = HealthResponse(
        status=overall_status,
        app_name=settings.APP_NAME,
        api_version="1.0.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
        database=DatabaseHealth(
            connected=db_connected,
            latency_ms=latency_ms,
            message=db_message,
        ),
        system=SystemInfo(
            python_version=sys.version.split()[0],
            environment=settings.APP_ENV,
            debug=settings.DEBUG,
        ),
    )

    return JSONResponse(status_code=status_code, content=payload.model_dump())
