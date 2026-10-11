from sqlalchemy import text
from app.db.base import Base
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
from app.models.user import User


def test_database_connection(db_session):
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1


def test_schema_table_names_registered():
    tables = Base.metadata.tables.keys()
    expected_tables = {
        "customers",
        "orders",
        "order_items",
        "order_payments",
        "order_reviews",
        "products",
        "sellers",
        "geolocation",
        "product_category_translation",
        "users",
    }
    for expected in expected_tables:
        assert expected in tables, f"Expected table {expected} not found in Base metadata"


def test_customer_model_instantiation(db_session):
    customer = Customer(
        customer_id="cust_001",
        customer_unique_id="unique_001",
        customer_zip_code_prefix=12345,
        customer_city="Sao Paulo",
        customer_state="SP",
    )
    db_session.add(customer)
    db_session.commit()

    retrieved = db_session.get(Customer, "cust_001")
    assert retrieved is not None
    assert retrieved.customer_city == "Sao Paulo"
    assert retrieved.customer_state == "SP"
