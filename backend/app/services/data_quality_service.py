import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models.olist import (
    Customer,
    Order,
    OrderItem,
    OrderPayment,
    OrderReview,
    Product,
    Seller,
    Geolocation,
    ProductCategoryTranslation,
)
from app.schemas.data_quality import (
    DataQualityReport,
    TableQualityMetric,
    ColumnQuality,
    DatasetFileStatus,
)

EXPECTED_RAW_FILES = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]

TARGET_TABLES = [
    Customer,
    Order,
    OrderItem,
    OrderPayment,
    OrderReview,
    Product,
    Seller,
    Geolocation,
    ProductCategoryTranslation,
]


def _format_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


class DataQualityService:
    @staticmethod
    def inspect_raw_files() -> List[DatasetFileStatus]:
        """Checks actual physical presence and size of raw CSV files."""
        # Check raw directory relative to cwd or backend
        candidates = [
            Path(settings.RAW_DATA_PATH),
            Path.cwd() / "data" / "raw",
            Path.cwd().parent / "data" / "raw",
            Path(__file__).resolve().parents[3] / "data" / "raw",
        ]
        raw_dir = candidates[0]
        for candidate in candidates:
            if candidate.exists():
                raw_dir = candidate
                break

        results: List[DatasetFileStatus] = []
        for filename in EXPECTED_RAW_FILES:
            file_path = raw_dir / filename
            if file_path.exists() and file_path.is_file():
                size = file_path.stat().st_size
                results.append(
                    DatasetFileStatus(
                        filename=filename,
                        exists=True,
                        size_bytes=size,
                        size_readable=_format_size(size),
                    )
                )
            else:
                results.append(
                    DatasetFileStatus(
                        filename=filename,
                        exists=False,
                        size_bytes=0,
                        size_readable="0 B",
                    )
                )
        return results

    @staticmethod
    def inspect_database_tables(db: Session) -> List[TableQualityMetric]:
        """Executes actual SQL inspection across all registered platform tables."""
        table_metrics: List[TableQualityMetric] = []
        inspector = inspect(engine)
        existing_table_names = set(inspector.get_table_names())

        for model_cls in TARGET_TABLES:
            table_name = model_cls.__tablename__

            if table_name not in existing_table_names:
                table_metrics.append(
                    TableQualityMetric(
                        table_name=table_name,
                        row_count=0,
                        column_count=len(model_cls.__table__.columns),
                        columns=[],
                        completeness_score=0.0,
                        status="table_missing",
                    )
                )
                continue

            # Row count check
            try:
                row_count_res = db.execute(text(f'SELECT COUNT(*) FROM "{table_name}"')).scalar()
                row_count = int(row_count_res or 0)
            except Exception:
                row_count = 0

            columns_info: List[ColumnQuality] = []
            total_null_pct = 0.0
            col_count = len(model_cls.__table__.columns)

            for col in model_cls.__table__.columns:
                null_count = 0
                null_pct = 0.0

                if row_count > 0 and col.nullable:
                    try:
                        null_res = db.execute(
                            text(f'SELECT COUNT(*) FROM "{table_name}" WHERE "{col.name}" IS NULL')
                        ).scalar()
                        null_count = int(null_res or 0)
                        null_pct = round((null_count / row_count) * 100, 2)
                    except Exception:
                        null_count = 0
                        null_pct = 0.0

                total_null_pct += null_pct
                columns_info.append(
                    ColumnQuality(
                        name=col.name,
                        data_type=str(col.type),
                        nullable=col.nullable,
                        null_count=null_count,
                        null_percentage=null_pct,
                    )
                )

            avg_null_pct = total_null_pct / col_count if col_count > 0 else 0.0
            completeness = round(max(0.0, 100.0 - avg_null_pct), 2) if row_count > 0 else 0.0

            status = "populated" if row_count > 0 else "empty"

            table_metrics.append(
                TableQualityMetric(
                    table_name=table_name,
                    row_count=row_count,
                    column_count=col_count,
                    columns=columns_info,
                    completeness_score=completeness,
                    status=status,
                )
            )

        return table_metrics

    @classmethod
    def generate_report(cls, db: Session) -> DataQualityReport:
        """Generates comprehensive real-time data quality report without mock data."""
        raw_files = cls.inspect_raw_files()
        table_metrics = cls.inspect_database_tables(db)

        files_found = sum(1 for f in raw_files if f.exists)
        files_total = len(raw_files)

        total_tables = len(table_metrics)
        populated_tables = sum(1 for t in table_metrics if t.row_count > 0)
        total_records = sum(t.row_count for t in table_metrics)

        warnings: List[str] = []
        if files_found == 0:
            warnings.append(
                "Raw Olist CSV files not detected in data/raw/. Run scripts/download_dataset.py or place CSVs to begin ingestion."
            )
        elif files_found < files_total:
            missing = [f.filename for f in raw_files if not f.exists]
            warnings.append(f"Missing {len(missing)} raw files: {', '.join(missing)}")

        if populated_tables == 0:
            warnings.append(
                "Database schema is established, but tables currently contain 0 records. Awaiting ETL data ingestion in Stage 2."
            )

        # Operational status assessment
        if populated_tables == total_tables and files_found == files_total:
            overall_status = "operational"
        elif files_found == 0 or populated_tables == 0:
            overall_status = "pending_ingestion"
        else:
            overall_status = "degraded"

        return DataQualityReport(
            status=overall_status,
            generated_at=datetime.now(timezone.utc).isoformat(),
            total_tables=total_tables,
            populated_tables=populated_tables,
            total_records=total_records,
            raw_files_found=files_found,
            raw_files_total=files_total,
            raw_files=raw_files,
            tables=table_metrics,
            pipeline_stage="Stage 1: Platform & Schema Foundation",
            warnings=warnings,
        )
