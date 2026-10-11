from app.services.data_quality_service import DataQualityService, EXPECTED_RAW_FILES
from app.models.olist import Customer, ProductCategoryTranslation, Product


def test_data_quality_endpoint_structure(client):
    response = client.get("/api/v1/data-quality")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "total_tables" in data
    assert data["total_tables"] == 9
    assert "populated_tables" in data
    assert "tables" in data
    assert len(data["tables"]) == 9
    assert "raw_files" in data
    assert len(data["raw_files"]) == len(EXPECTED_RAW_FILES)


def test_data_quality_service_real_counts(db_session):
    # Verify report accurately reports row counts when records are inserted
    report_initial = DataQualityService.generate_report(db_session)
    assert report_initial.total_records == 0

    # Insert valid records
    category = ProductCategoryTranslation(
        product_category_name="beleza_saude",
        product_category_name_english="health_beauty",
    )
    product = Product(
        product_id="prod_001",
        product_category_name="beleza_saude",
        product_weight_g=500.0,
    )
    db_session.add(category)
    db_session.add(product)
    db_session.commit()

    report_after = DataQualityService.generate_report(db_session)
    assert report_after.total_records == 2
    
    prod_table = next(t for t in report_after.tables if t.table_name == "products")
    assert prod_table.row_count == 1
    assert prod_table.status == "populated"


def test_data_validation_constraints(db_session):
    # Test primary key uniqueness constraint
    c1 = Customer(
        customer_id="duplicate_id",
        customer_unique_id="unique_a",
        customer_zip_code_prefix=11000,
        customer_city="Santos",
        customer_state="SP",
    )
    db_session.add(c1)
    db_session.commit()

    # Attempt inserting duplicate PK
    import pytest
    from sqlalchemy.exc import IntegrityError
    c2 = Customer(
        customer_id="duplicate_id",
        customer_unique_id="unique_b",
        customer_zip_code_prefix=11000,
        customer_city="Santos",
        customer_state="SP",
    )
    db_session.add(c2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
