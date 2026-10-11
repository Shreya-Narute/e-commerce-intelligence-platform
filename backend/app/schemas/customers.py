from typing import Optional
from pydantic import BaseModel


class CustomerSummary(BaseModel):
    total_unique_customers: int = 0
    avg_orders_per_customer: Optional[float] = None
    avg_spend_per_customer: Optional[float] = None
    status: str = "no_data"


class CustomersByState(BaseModel):
    state: str
    unique_customers: int


class PurchaseFrequency(BaseModel):
    order_count: int
    customer_count: int


class CustomerCohort(BaseModel):
    cohort_month: str
    new_customers: int
