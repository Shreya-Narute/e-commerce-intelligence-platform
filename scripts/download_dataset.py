"""
Download helper for Brazilian E-Commerce Public Dataset by Olist.

This script explains how to acquire the dataset or can download it using Kaggle CLI.
"""
import os
import sys
import shutil
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)

REQUIRED_FILES = [
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


def check_status():
    print(f"Checking data directory: {DATA_DIR}")
    found = 0
    for filename in REQUIRED_FILES:
        target = DATA_DIR / filename
        if target.exists():
            print(f"  [OK] {filename} ({target.stat().st_size:,} bytes)")
            found += 1
        else:
            print(f"  [MISSING] {filename}")
    
    print(f"\nStatus: {found}/{len(REQUIRED_FILES)} files present.")
    if found < len(REQUIRED_FILES):
        print("\nTo obtain the dataset:")
        print("1. Using Kaggle CLI:")
        print("   kaggle datasets download -d olistbr/brazilian-ecommerce -p data/raw --unzip")
        print("\n2. Direct Web Download:")
        print("   Visit https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce")
        print("   Extract all CSV files directly into the 'data/raw/' folder.")


if __name__ == "__main__":
    check_status()
