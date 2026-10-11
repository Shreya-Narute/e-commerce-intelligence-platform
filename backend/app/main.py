from contextlib import asynccontextmanager
import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models import (
    Customer,
    Order,
    OrderItem,
    OrderPayment,
    OrderReview,
    Product,
    Seller,
    Geolocation,
    ProductCategoryTranslation,
    User,
)
from app.services.auth_service import AuthService
from app.api.v1.router import api_router

logger = logging.getLogger(__name__)


def _warm_rfm_cache() -> None:
    """Pre-compute RFM result in a background thread so the first browser request
    hits a warm cache instead of waiting 20+ seconds."""
    try:
        from app.analytics import rfm as rfm_mod
        with SessionLocal() as db:
            result = rfm_mod.compute_rfm(db)
            if result.get("status") == "ok":
                logger.info(
                    "[Startup] RFM cache warmed: %d customers, %d segments",
                    result.get("total_customers", 0),
                    len(result.get("segments", [])),
                )
            else:
                logger.info("[Startup] RFM cache warm-up skipped: status=%s", result.get("status"))
    except Exception as exc:
        logger.warning("[Startup] RFM cache warm-up failed (non-fatal): %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Attempt to bootstrap tables and seed admin user on startup
    try:
        # Schema managed by Alembic migrations - do not use create_all in production
        # Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            AuthService.seed_initial_admin(db)
    except Exception as exc:
        print(f"[Lifespan Notice] Database initialization deferred: {exc}")

    # Warm the RFM cache in the background so the first page load is fast
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, _warm_rfm_cache)

    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Production-grade E-Commerce Intelligence & Decision Support Platform API. "
        "Provides comprehensive health monitoring, data quality auditing, authentication, "
        "and analytical foundation for the Brazilian E-Commerce (Olist) dataset."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS if settings.BACKEND_CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
def root():
    return {
        "service": settings.APP_NAME,
        "status": "online",
        "documentation": "/docs",
        "api_v1": settings.API_V1_PREFIX,
        "health_check": f"{settings.API_V1_PREFIX}/health",
        "data_quality": f"{settings.API_V1_PREFIX}/data-quality",
    }
