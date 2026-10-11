from typing import Any, List, Optional
from pydantic import BaseModel, Field


class SellerSummary(BaseModel):
    total_sellers: int
    avg_revenue_per_seller: Optional[float]


class TopRevenueSeller(BaseModel):
    seller_id: str
    seller_state: str
    total_revenue: float
    order_count: int


class SellerByState(BaseModel):
    state: str
    seller_count: int
    total_revenue: float


class SellerPerformance(BaseModel):
    seller_id: str
    seller_state: str
    avg_review_score: Optional[float]
    avg_delivery_days: Optional[float]
    order_count: int


class SellersResponse(BaseModel):
    status: str = Field(description="'ok' or 'no_data'")
    message: str = ""
    data: Any = None
