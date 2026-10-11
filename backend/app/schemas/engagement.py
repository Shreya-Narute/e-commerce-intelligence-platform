from typing import Any, List, Optional
from pydantic import BaseModel, Field


class EngagementRiskTier(BaseModel):
    tier: str  # Active, Cooling, At Risk, Inactive
    customer_count: int
    description: str


class AtRiskCustomer(BaseModel):
    customer_unique_id: str
    last_purchase_date: str
    days_since_purchase: int
    tier: str


class EngagementRiskSummaryResponse(BaseModel):
    status: str = "ok"
    message: str = ""
    reference_date: Optional[str] = None
    data: List[EngagementRiskTier] = []


class AtRiskCustomersResponse(BaseModel):
    status: str = "ok"
    message: str = ""
    total: int = 0
    page: int = 1
    page_size: int = 50
    data: List[AtRiskCustomer] = []
