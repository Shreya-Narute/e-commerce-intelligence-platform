from typing import Any, List, Optional
from pydantic import BaseModel, Field


class PaymentSummary(BaseModel):
    total_payment_value: float
    avg_installments: Optional[float]
    payment_type_breakdown: List[dict]


class InstallmentBucket(BaseModel):
    installments: str  # "1", "2", ..., "12+"
    count: int


class MonthlyPaymentVolume(BaseModel):
    year_month: str
    total_value: float
    transaction_count: int


class PaymentsResponse(BaseModel):
    status: str = Field(description="'ok' or 'no_data'")
    message: str = ""
    data: Any = None
