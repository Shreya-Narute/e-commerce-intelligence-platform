from typing import Any, List, Optional
from pydantic import BaseModel, Field


class ForecastPoint(BaseModel):
    period: str  # YYYY-MM
    forecast: float
    lower_bound: float
    upper_bound: float


class ForecastResponse(BaseModel):
    status: str = Field(description="'ok', 'no_data', or 'insufficient_data'")
    message: str = ""
    mae: Optional[float] = None
    rmse: Optional[float] = None
    mape: Optional[float] = None
    forecast: List[ForecastPoint] = []
    historical: List[dict] = []
