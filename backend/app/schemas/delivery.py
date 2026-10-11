from typing import Any, List, Optional
from pydantic import BaseModel, Field


class DeliverySummary(BaseModel):
    avg_delivery_days: Optional[float]
    on_time_rate: Optional[float]
    avg_review_score: Optional[float]
    total_delivered_orders: int


class DeliveryByState(BaseModel):
    state: str
    avg_delivery_days: float
    order_count: int


class ReviewDistribution(BaseModel):
    review_score: int
    count: int


class LateAnalysis(BaseModel):
    on_time_count: int
    late_count: int
    on_time_avg_review: Optional[float]
    late_avg_review: Optional[float]


class DeliveryResponse(BaseModel):
    status: str = Field(description="'ok' or 'no_data'")
    message: str = ""
    data: Any = None
