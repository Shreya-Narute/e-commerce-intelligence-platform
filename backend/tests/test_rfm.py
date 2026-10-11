"""Tests for the RFM analytics service (direct function calls, not the API).

The RFM module (app.analytics.rfm) caches the last "ok" result in-process for
1 hour, so each test clears ``rfm._CACHE`` before computing to avoid stale
results leaking between tests.

Data caveat (D3 in the plan): compute_rfm returns ``insufficient_data`` for
fewer than 10 customers and ``no_data`` on an empty database. We exercise both,
plus a >=12-customer fixture that triggers full quintile scoring + K-Means.

These tests import numpy / pandas / scikit-learn, so they can only run where
those packages are installed (the Docker backend container). Locally the
backend pytest suite cannot even be collected due to the missing packages.
"""
from datetime import datetime, timedelta

from app.analytics import rfm as rfm_analytics
from app.models.olist import Customer, Order, OrderPayment

# All valid segment labels produced by rfm._label()
EXPECTED_SEGMENTS = {
    "Champions",
    "Loyal Customers",
    "At Risk",
    "Lost",
    "New Customers",
    "Potential Loyalists",
    "Others",
}

# (frequency, [months_ago for each order], payment_value per order)
_RFM_SPECS = [
    (1, [0], 500.0),
    (1, [1], 120.0),
    (1, [2], 80.0),
    (2, [0, 3], 300.0),
    (2, [1, 4], 250.0),
    (1, [5], 60.0),
    (3, [0, 2, 6], 900.0),
    (1, [7], 40.0),
    (2, [3, 8], 150.0),
    (1, [9], 200.0),
    (2, [6, 10], 110.0),
    (1, [11], 30.0),
]


def _insert_customers(db_session, count):
    """Insert `count` customers (up to 12) with varied recency/frequency/monetary."""
    base_date = datetime(2018, 1, 15, 10, 0, 0)
    inserted_unique_ids = []
    for i in range(1, count + 1):
        cust_uid = f"rfm_uid_{i}"
        cust_id = f"rfm_cid_{i}"
        inserted_unique_ids.append(cust_uid)
        customer = Customer(
            customer_id=cust_id,
            customer_unique_id=cust_uid,
            customer_zip_code_prefix=10000 + i,
            customer_city="Sao Paulo",
            customer_state="SP",
        )
        db_session.add(customer)
        freq, months_ago_list, payment = _RFM_SPECS[i - 1]
        for seq, months_ago in enumerate(months_ago_list, start=1):
            purchase = base_date - timedelta(days=30 * months_ago)
            order = Order(
                order_id=f"rfm_oid_{i}_{seq}",
                customer_id=cust_id,
                order_status="delivered",
                order_purchase_timestamp=purchase,
                order_estimated_delivery_date=purchase + timedelta(days=10),
            )
            pay = OrderPayment(
                order_id=f"rfm_oid_{i}_{seq}",
                payment_sequential=1,
                payment_type="credit_card",
                payment_installments=1,
                payment_value=payment,
            )
            db_session.add_all([order, pay])
    db_session.commit()
    return inserted_unique_ids


def test_rfm_no_data(db_session):
    rfm_analytics._CACHE.clear()
    result = rfm_analytics.compute_rfm(db_session)
    assert result["status"] == "no_data"
    assert result["data"] == []


def test_rfm_insufficient_data(db_session):
    rfm_analytics._CACHE.clear()
    _insert_customers(db_session, count=3)
    result = rfm_analytics.compute_rfm(db_session)
    assert result["status"] == "insufficient_data"
    assert result["data"] == []


def test_rfm_full_computation(db_session):
    rfm_analytics._CACHE.clear()
    inserted = _insert_customers(db_session, count=12)
    assert len(inserted) == 12

    result = rfm_analytics.compute_rfm(db_session)
    assert result["status"] == "ok"
    assert result["total_customers"] == 12

    customers = result["customers"]
    assert len(customers) == 12

    # Every R/F/M score must be in 1..5
    for row in customers:
        assert 1 <= row["r_score"] <= 5
        assert 1 <= row["f_score"] <= 5
        assert 1 <= row["m_score"] <= 5
        # Segment must be one of the known labels
        assert row["segment"] in EXPECTED_SEGMENTS

    # Segments summary is non-empty and uses only known labels
    segments = result["segments"]
    assert isinstance(segments, list) and len(segments) > 0
    for seg in segments:
        assert seg["segment"] in EXPECTED_SEGMENTS
        assert seg["customer_count"] >= 1

    # K-Means produced <= 4 clusters, all cluster ids in 0..3
    clusters = {row["cluster"] for row in customers}
    assert len(clusters) <= 4
    assert all(0 <= c <= 3 for c in clusters)

    # Silhouette score is either None (<=4 customers) or a float in [-1, 1]
    sil = result["silhouette_score"]
    if sil is not None:
        assert -1.0 <= float(sil) <= 1.0


def test_rfm_cache_is_populated_after_ok(db_session):
    """A successful run is cached; a second call (even on an empty session)
    returns the cached result, which is why every test clears the cache first."""
    rfm_analytics._CACHE.clear()
    _insert_customers(db_session, count=12)
    first = rfm_analytics.compute_rfm(db_session)
    assert first["status"] == "ok"
    assert rfm_analytics._CACHE.get("rfm") is not None
