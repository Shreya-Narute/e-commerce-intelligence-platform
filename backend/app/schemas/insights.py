from typing import Any, List, Optional
from pydantic import BaseModel, Field


class InsightItem(BaseModel):
    title: str
    value: str
    context: str
    recommendation: str


class InsightsSummaryResponse(BaseModel):
    status: str = Field(description="'ok' or 'no_data'")
    message: str = ""
    insights: List[InsightItem] = []
