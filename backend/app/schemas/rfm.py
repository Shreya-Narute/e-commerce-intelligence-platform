from typing import Any, List, Optional
from pydantic import BaseModel, Field


class RFMSegment(BaseModel):
    segment: str
    customer_count: int
    avg_recency_days: float
    avg_frequency: float
    avg_monetary: float


class RFMScoreDistribution(BaseModel):
    score: int = Field(ge=1, le=5)
    r_count: int
    f_count: int
    m_count: int


class RFMCustomer(BaseModel):
    customer_unique_id: str
    recency_days: int
    frequency: int
    monetary: float
    r_score: int
    f_score: int
    m_score: int
    segment: str
    cluster: int


class RFMCustomersResponse(BaseModel):
    status: str = "ok"
    message: str = ""
    total: int = 0
    page: int = 1
    page_size: int = 50
    data: List[RFMCustomer] = []


class RFMResponse(BaseModel):
    status: str = Field(description="'ok', 'no_data', or 'insufficient_data'")
    message: str = ""
    data: Any = None
