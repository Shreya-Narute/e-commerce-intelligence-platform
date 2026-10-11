from typing import Optional
from pydantic import BaseModel


class TopRevenueProduct(BaseModel):
    product_id: str
    category_name: Optional[str] = None
    revenue: float
    order_count: int


class CategorySummary(BaseModel):
    category_name: str
    order_count: int
    revenue: float


class CategoryTrendPoint(BaseModel):
    year_month: str
    category_name: str
    order_count: int


class ProductDimensions(BaseModel):
    category_name: str
    avg_weight_g: Optional[float] = None
    avg_length_cm: Optional[float] = None
    avg_height_cm: Optional[float] = None
    avg_width_cm: Optional[float] = None
