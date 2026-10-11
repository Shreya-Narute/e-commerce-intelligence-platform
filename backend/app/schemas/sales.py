from typing import Any, List, Optional
from pydantic import BaseModel, Field


class SalesSummary(BaseModel):
    total_revenue: Optional[float] = None
    total_orders: int = 0
    average_order_value: Optional[float] = None
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None
    status: str = "no_data"


class MonthlyRevenue(BaseModel):
    year_month: str = Field(description="Format: YYYY-MM")
    revenue: float
    order_count: int


class RevenueByState(BaseModel):
    state: str
    revenue: float
    order_count: int


class RevenueByCategory(BaseModel):
    category_name: str
    revenue: float
    order_count: int


class OrderStatusCount(BaseModel):
    status: str
    count: int


class PaymentTypeRevenue(BaseModel):
    payment_type: str
    revenue: float
    transaction_count: int


class SalesResponse(BaseModel):
    status: str = Field(description="'ok' or 'no_data'")
    message: str = ""
    data: Any = None
