"""Tests for the Sales Analytics API (/api/v1/sales).

Uses the shared `client` fixture from conftest.py and a small auth helper to
obtain the seeded admin JWT. Synthetic rows are inserted through the shared
`db_session` fixture so the API (which receives the same session via the
get_db override) sees them.
"""
from datetime import datetime

from app.models.olist import Customer, Order, OrderPayment


def _auth_headers(client):
    """Log in as the seeded admin and return an Authorization header dict."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@ecommerce-intel.io", "password": "Admin123!"},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Empty database
# ---------------------------------------------------------------------------

def test_sales_summary_no_data(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/sales/summary", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "no_data"
    assert data["data"]["total_orders"] == 0


def test_sales_monthly_no_data(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/sales/monthly", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "no_data"
    assert data["data"] == []


def test_sales_by_state_no_data(client):
    headers = _auth_headers(client)
    response = client.get("/api/v1/sales/by-state", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "no_data"
    assert data["data"] == []


def test_sales_summary_requires_auth(client):
    # No Authorization header -> 401, never 500
    response = client.get("/api/v1/sales/summary")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# With synthetic data
# ---------------------------------------------------------------------------

def test_sales_endpoints_with_data(client, db_session):
    headers = _auth_headers(client)

    customer = Customer(
        customer_id="cust_sales_1",
        customer_unique_id="unique_sales_1",
        customer_zip_code_prefix=1000,
        customer_city="Sao Paulo",
        customer_state="SP",
    )
    order1 = Order(
        order_id="order_sales_1",
        customer_id="cust_sales_1",
        order_status="delivered",
        order_purchase_timestamp=datetime(2018, 1, 15, 10, 0, 0),
        order_estimated_delivery_date=datetime(2018, 1, 25, 10, 0, 0),
    )
    order2 = Order(
        order_id="order_sales_2",
        customer_id="cust_sales_1",
        order_status="delivered",
        order_purchase_timestamp=datetime(2018, 2, 20, 10, 0, 0),
        order_estimated_delivery_date=datetime(2018, 3, 1, 10, 0, 0),
    )
    payment1 = OrderPayment(
        order_id="order_sales_1",
        payment_sequential=1,
        payment_type="credit_card",
        payment_installments=1,
        payment_value=100.00,
    )
    payment2 = OrderPayment(
        order_id="order_sales_2",
        payment_sequential=1,
        payment_type="credit_card",
        payment_installments=1,
        payment_value=200.00,
    )
    db_session.add_all([customer, order1, order2, payment1, payment2])
    db_session.commit()

    # Summary: revenue = 300, orders = 2, AOV = 150
    response = client.get("/api/v1/sales/summary", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "ok"
    assert data["data"]["total_revenue"] == 300.00
    assert data["data"]["total_orders"] == 2
    assert data["data"]["average_order_value"] == 150.00

    # Monthly: two distinct months
    response = client.get("/api/v1/sales/monthly", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "ok"
    assert len(data["data"]) == 2
    assert data["data"][0]["year_month"] == "2018-01"
    assert data["data"][1]["year_month"] == "2018-02"

    # By state: one row for SP
    response = client.get("/api/v1/sales/by-state", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "ok"
    assert len(data["data"]) == 1
    assert data["data"][0]["state"] == "SP"
    assert data["data"][0]["revenue"] == 300.00
    assert data["data"][0]["order_count"] == 2
