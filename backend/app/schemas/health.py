from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class DatabaseHealth(BaseModel):
    connected: bool
    latency_ms: float
    message: str


class SystemInfo(BaseModel):
    python_version: str
    environment: str
    debug: bool


class HealthResponse(BaseModel):
    status: str = Field(description="'healthy' when all checks pass, 'degraded' if db fails")
    app_name: str
    api_version: str
    timestamp: str
    database: DatabaseHealth
    system: SystemInfo
