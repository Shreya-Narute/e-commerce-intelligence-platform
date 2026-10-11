from fastapi import APIRouter

from app.api.v1 import (
    health,
    data_quality,
    auth,
    sales,
    products,
    customers,
    data_explorer,
    rfm,
    sellers,
    delivery,
    payments,
    engagement,
    forecasting,
    model_eval,
    insights,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(data_quality.router, tags=["Data Quality"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(sales.router, prefix="/sales", tags=["Sales"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(data_explorer.router, prefix="/data-explorer", tags=["Data Explorer"])
api_router.include_router(rfm.router, prefix="/rfm", tags=["RFM"])
api_router.include_router(sellers.router, prefix="/sellers", tags=["Sellers"])
api_router.include_router(delivery.router, prefix="/delivery", tags=["Delivery"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(engagement.router, prefix="/engagement", tags=["Engagement"])
api_router.include_router(forecasting.router, prefix="/forecasting", tags=["Forecasting"])
api_router.include_router(model_eval.router, prefix="/model-eval", tags=["Model Evaluation"])
api_router.include_router(insights.router, prefix="/insights", tags=["Insights"])
