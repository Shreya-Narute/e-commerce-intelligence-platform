from typing import Any, List, Optional
from pydantic import BaseModel, Field


class RFMModelEval(BaseModel):
    status: str
    silhouette_score: Optional[float] = None
    cluster_sizes: Optional[dict] = None
    segment_distribution: Optional[dict] = None
    message: str = ""


class ForecastingModelEval(BaseModel):
    status: str
    mae: Optional[float] = None
    rmse: Optional[float] = None
    mape: Optional[float] = None
    message: str = ""
