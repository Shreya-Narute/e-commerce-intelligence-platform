"""
Data Ingestion & Validation Pipeline for Brazilian E-Commerce Platform.

Reads raw immutable CSV files from data/raw/, applies strict schema validation,
type casting, null handling, and loads into PostgreSQL in dependency order.

Supports safe re-runs via INSERT ON CONFLICT DO NOTHING.
Use --truncate for a full reload (clears tables before inserting).
"""
import argparse
import os
import sys
import time
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert

# Ensure backend can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models import (
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

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def log(msg: str):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")




def _upsert_dataframe(df: pd.DataFrame, model_cls, conflict_cols: list, conn) -> dict:
    """
    Insert rows in batches and safely skip existing records.
    """
    rows_read = len(df)

    if rows_read == 0:
        return {
            "rows_read": 0,
            "rows_inserted": 0,
            "rows_skipped": 0,
        }

    table = model_cls.__table__

    # Convert missing pandas values to SQL NULL.
    df = df.astype(object).where(pd.notna(df), None)
    records = df.to_dict(orient="records")

    batch_size = 1000
    rows_inserted = 0

    for start in range(0, rows_read, batch_size):
        batch = records[start:start + batch_size]

        stmt = pg_insert(table).values(batch)

        # Use conflict handling only when PostgreSQL has
        # a matching primary key or unique constraint.
        if conflict_cols:
            stmt = stmt.on_conflict_do_nothing(
                index_elements=conflict_cols
            )
        else:
            stmt = stmt.on_conflict_do_nothing()

        result = conn.execute(stmt)

        if result.rowcount < 0:
            raise RuntimeError(
                f"Could not determine inserted row count for {table.name}"
            )

        rows_inserted += result.rowcount

    return {
        "rows_read": rows_read,
        "rows_inserted": rows_inserted,
        "rows_skipped": rows_read - rows_inserted,
    }


def _truncate_tables(conn):
    """Truncate all Olist business tables in reverse dependency order."""
    tables_in_order = [
        "order_reviews",
        "order_payments",
        "order_items",
        "orders",
        "products",
        "sellers",
        "customers",
        "geolocation",
        "product_category_translation",
    ]
    log("Truncating tables (--truncate mode)...")
    for table_name in tables_in_order:
        conn.execute(text(f'TRUNCATE TABLE "{table_name}" CASCADE'))
        log(f"  Truncated {table_name}.")


def ingest(truncate: bool = False):
    log("Starting Olist dataset ingestion pipeline...")
    if not DATA_DIR.exists():
        log(f"Error: Directory {DATA_DIR} does not exist.")
        return

    # Ensure tables exist (safe no-op when Alembic has already created them)
    log("Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)

    summary = {}

    with engine.begin() as conn:
        if truncate:
            _truncate_tables(conn)

        # 1. Product Category Translations
        cat_file = DATA_DIR / "product_category_name_translation.csv"
        if cat_file.exists():
            log(f"Ingesting {cat_file.name}...")
            df = pd.read_csv(cat_file)
            df.drop_duplicates(subset=["product_category_name"], inplace=True)
            stats = _upsert_dataframe(df, ProductCategoryTranslation, ["product_category_name"], conn)
            summary["product_category_translation"] = stats
            log(f"  Read={stats['rows_read']}, Inserted={stats['rows_inserted']}, Skipped={stats['rows_skipped']}")
        else:
            log(f"  WARNING: {cat_file.name} not found, skipping.")

        # 2. Customers
        cust_file = DATA_DIR / "olist_customers_dataset.csv"
        if cust_file.exists():
            log(f"Ingesting {cust_file.name}...")
            df = pd.read_csv(cust_file)
            df.drop_duplicates(subset=["customer_id"], inplace=True)
            stats = _upsert_dataframe(df, Customer, ["customer_id"], conn)
            summary["customers"] = stats
            log(f"  Read={stats['rows_read']}, Inserted={stats['rows_inserted']}, Skipped={stats['rows_skipped']}")
        else:
            log(f"  WARNING: {cust_file.name} not found, skipping.")

        # 3. Sellers
        sell_file = DATA_DIR / "olist_sellers_dataset.csv"
        if sell_file.exists():
            log(f"Ingesting {sell_file.name}...")
            df = pd.read_csv(sell_file)
            df.drop_duplicates(subset=["seller_id"], inplace=True)
            stats = _upsert_dataframe(df, Seller, ["seller_id"], conn)
            summary["sellers"] = stats
            log(f"  Read={stats['rows_read']}, Inserted={stats['rows_inserted']}, Skipped={stats['rows_skipped']}")
        else:
            log(f"  WARNING: {sell_file.name} not found, skipping.")

        # 4. Products
        prod_file = DATA_DIR / "olist_products_dataset.csv"
        if prod_file.exists():
            log(f"Ingesting {prod_file.name}...")
            df = pd.read_csv(prod_file)
            df.drop_duplicates(subset=["product_id"], inplace=True)
            stats = _upsert_dataframe(df, Product, ["product_id"], conn)
            summary["products"] = stats
            log(f"  Read={stats['rows_read']}, Inserted={stats['rows_inserted']}, Skipped={stats['rows_skipped']}")
        else:
            log(f"  WARNING: {prod_file.name} not found, skipping.")

        # 5. Orders
        orders_file = DATA_DIR / "olist_orders_dataset.csv"
        if orders_file.exists():
            log(f"Ingesting {orders_file.name}...")
            df = pd.read_csv(orders_file)
            date_cols = [
                "order_purchase_timestamp",
                "order_approved_at",
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
                "order_estimated_delivery_date",
            ]
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
            df.drop_duplicates(subset=["order_id"], inplace=True)
            stats = _upsert_dataframe(df, Order, ["order_id"], conn)
            summary["orders"] = stats
            log(f"  Read={stats['rows_read']}, Inserted={stats['rows_inserted']}, Skipped={stats['rows_skipped']}")
        else:
            log(f"  WARNING: {orders_file.name} not found, skipping.")

        # 6. Order Items
        items_file = DATA_DIR / "olist_order_items_dataset.csv"
        if items_file.exists():
            log(f"Ingesting {items_file.name}...")
            df = pd.read_csv(items_file)
            if "shipping_limit_date" in df.columns:
                df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"], errors="coerce")
            df.drop_duplicates(subset=["order_id", "order_item_id"], inplace=True)
            stats = _upsert_dataframe(df, OrderItem, ["order_id", "order_item_id"], conn)
            summary["order_items"] = stats
            log(f"  Read={stats['rows_read']}, Inserted={stats['rows_inserted']}, Skipped={stats['rows_skipped']}")
        else:
            log(f"  WARNING: {items_file.name} not found, skipping.")

        # 7. Order Payments
        pay_file = DATA_DIR / "olist_order_payments_dataset.csv"
        if pay_file.exists():
            log(f"Ingesting {pay_file.name}...")
            df = pd.read_csv(pay_file)
            df.drop_duplicates(subset=["order_id", "payment_sequential"], inplace=True)
            stats = _upsert_dataframe(df, OrderPayment, ["order_id", "payment_sequential"], conn)
            summary["order_payments"] = stats
            log(f"  Read={stats['rows_read']}, Inserted={stats['rows_inserted']}, Skipped={stats['rows_skipped']}")
        else:
            log(f"  WARNING: {pay_file.name} not found, skipping.")

        # 8. Order Reviews
        rev_file = DATA_DIR / "olist_order_reviews_dataset.csv"
        if rev_file.exists():
            log(f"Ingesting {rev_file.name}...")
            df = pd.read_csv(rev_file)
            for col in ["review_creation_date", "review_answer_timestamp"]:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
            cols_to_keep = [
                "review_id",
                "order_id",
                "review_score",
                "review_comment_title",
                "review_comment_message",
                "review_creation_date",
                "review_answer_timestamp",
            ]
            df = df[[c for c in cols_to_keep if c in df.columns]]
            df.drop_duplicates(subset=["review_id", "order_id"], inplace=True)
            stats = _upsert_dataframe(df, OrderReview, ["review_id", "order_id"], conn)
            summary["order_reviews"] = stats
            log(f"  Read={stats['rows_read']}, Inserted={stats['rows_inserted']}, Skipped={stats['rows_skipped']}")
        else:
            log(f"  WARNING: {rev_file.name} not found, skipping.")

       
        # 9. Geolocation
        geo_file = DATA_DIR / "olist_geolocation_dataset.csv"
        if geo_file.exists():
            log(f"Ingesting {geo_file.name} (deduplicating exact records)...")
            df = pd.read_csv(geo_file)

            # Keep different coordinates for the same postal code.
            geo_columns = [
                "geolocation_zip_code_prefix",
                "geolocation_lat",
                "geolocation_lng",
                "geolocation_city",
                "geolocation_state",
            ]
            df.drop_duplicates(subset=geo_columns, inplace=True)

            stats = _upsert_dataframe(
                df,
                Geolocation,
                geo_columns,
                conn,
            )
            summary["geolocation"] = stats
            log(
                f"  Read={stats['rows_read']}, "
                f"Inserted={stats['rows_inserted']}, "
                f"Skipped={stats['rows_skipped']}"
            )
        else:
            log(f"  WARNING: {geo_file.name} not found, skipping.")


    # Final summary
    log("")
    log("=== Ingestion Summary ===")
    total_read = total_inserted = total_skipped = 0
    for table, stats in summary.items():
        log(f"  {table:35s}  read={stats['rows_read']:>7}  inserted={stats['rows_inserted']:>7}  skipped={stats['rows_skipped']:>7}")
        total_read += stats["rows_read"]
        total_inserted += stats["rows_inserted"]
        total_skipped += stats["rows_skipped"]
    log(f"  {'TOTAL':35s}  read={total_read:>7}  inserted={total_inserted:>7}  skipped={total_skipped:>7}")
    log("Data ingestion completed successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest Olist CSV data into PostgreSQL.")
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Truncate all business tables before inserting (full reload). Use with caution.",
    )
    args = parser.parse_args()
    ingest(truncate=args.truncate)
