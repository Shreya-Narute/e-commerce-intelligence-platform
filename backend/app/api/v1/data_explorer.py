from typing import Optional
from datetime import date, datetime
import decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User

router = APIRouter()

# Only these approved business tables can be browsed.
_ALLOWED_TABLES = {
    "customers",
    "sellers",
    "products",
    "orders",
    "order_items",
    "order_payments",
    "order_reviews",
    "geolocation",
    "product_category_translation",
    "users",
}


@router.get(
    "/tables",
    summary="List Available Tables",
    description="Returns approved public tables with their estimated row counts.",
)
def list_tables(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    # List only approved tables that actually exist in the public schema.
    rows = db.execute(
        text(
            """
            SELECT
                t.table_name,
                COALESCE(s.n_live_tup, 0) AS row_count
            FROM information_schema.tables AS t
            LEFT JOIN pg_stat_user_tables AS s
                ON s.schemaname = t.table_schema
                AND s.relname = t.table_name
            WHERE t.table_schema = 'public'
              AND t.table_type = 'BASE TABLE'
              AND t.table_name IN (
                  'customers',
                  'sellers',
                  'products',
                  'orders',
                  'order_items',
                  'order_payments',
                  'order_reviews',
                  'geolocation',
                  'product_category_translation',
                  'users'
              )
            ORDER BY t.table_name
            """
        )
    ).fetchall()

    data = [
        {
            "table_name": row[0],
            "row_count": int(row[1] or 0),
        }
        for row in rows
    ]

    return {
        "status": "ok",
        "message": "",
        "data": data,
    }


@router.get(
    "/{table_name}",
    summary="Browse Table Rows",
    description="Returns paginated rows from an approved business table.",
)
def browse_table(
    table_name: str,
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(
        default=50,
        ge=1,
        le=100,
        description="Rows per page (maximum 100)",
    ),
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    # Reject internal or unapproved tables.
    if table_name not in _ALLOWED_TABLES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table '{table_name}' not found or not accessible.",
        )

    # Confirm the approved table exists before querying it.
    exists = db.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
                  AND table_name = :table_name
            )
            """
        ),
        {"table_name": table_name},
    ).scalar()

    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table '{table_name}' does not exist.",
        )

    offset = (page - 1) * page_size

    total_rows = db.execute(
        text(f"SELECT COUNT(*) FROM public.{table_name}")
    ).scalar()

    result = db.execute(
        text(
            f"SELECT * FROM public.{table_name} "
            "LIMIT :limit OFFSET :offset"
        ),
        {"limit": page_size, "offset": offset},
    )

    columns = list(result.keys())
    rows = [dict(zip(columns, row)) for row in result.fetchall()]

    def jsonify(value):
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, decimal.Decimal):
            return float(value)
        return value

    rows = [
        {key: jsonify(value) for key, value in row.items()}
        for row in rows
    ]

    return {
        "status": "ok",
        "message": "",
        "table_name": table_name,
        "page": page,
        "page_size": page_size,
        "total_rows": int(total_rows or 0),
        "columns": columns,
        "data": rows,
    }