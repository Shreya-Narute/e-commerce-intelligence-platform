from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class ColumnQuality(BaseModel):
    name: str
    data_type: str
    nullable: bool
    null_count: int = 0
    null_percentage: float = 0.0


class TableQualityMetric(BaseModel):
    table_name: str
    row_count: int
    column_count: int
    columns: List[ColumnQuality] = []
    completeness_score: float = Field(
        ...,
        description="Percentage of cells populated (100.0 - avg null rate)",
        ge=0.0,
        le=100.0,
    )
    status: str = Field(description="'populated', 'empty', or 'table_missing'")


class DatasetFileStatus(BaseModel):
    filename: str
    exists: bool
    size_bytes: int
    size_readable: str


class DataQualityReport(BaseModel):
    status: str = Field(description="'operational', 'pending_ingestion', or 'degraded'")
    generated_at: str
    total_tables: int
    populated_tables: int
    total_records: int
    raw_files_found: int
    raw_files_total: int
    raw_files: List[DatasetFileStatus]
    tables: List[TableQualityMetric]
    pipeline_stage: str = "Stage 1: Platform & Schema Foundation"
    warnings: List[str] = []
