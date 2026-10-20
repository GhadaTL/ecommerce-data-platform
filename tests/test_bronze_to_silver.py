
import pandas as pd
import pytest

from src.etl import bronze_to_silver as pipeline


@pytest.fixture
def setup_directories(tmp_path, monkeypatch):
    """Use temporary directories instead of real project data."""
    bronze_dir = tmp_path / "bronze"
    silver_dir = tmp_path / "silver"

    bronze_dir.mkdir()
    silver_dir.mkdir()

    monkeypatch.setattr(pipeline, "BRONZE_DIR", bronze_dir)
    monkeypatch.setattr(pipeline, "SILVER_DIR", silver_dir)

    return bronze_dir, silver_dir


def test_invalid_dates_are_detected(setup_directories):
    bronze_dir, silver_dir = setup_directories

    filename = "olist_orders_dataset.csv"

    df = pd.DataFrame({
        "order_purchase_timestamp": ["2026-01-10 10:00:00"],
        "order_approved_at": ["not-a-date"],
        "order_delivered_carrier_date": [None],
        "order_delivered_customer_date": [None],
        "order_estimated_delivery_date": [None],
    })

    df.to_csv(bronze_dir / filename, index=False)

    result = pipeline.transform_to_silver(filename)

    assert result["invalid_dates"]["order_purchase_timestamp"] == 0
    assert result["invalid_dates"]["order_approved_at"] == 1

    output = pd.read_csv(silver_dir / filename)

    assert pd.isna(output.loc[0, "order_approved_at"])


def test_geolocation_duplicates_are_removed(setup_directories):
    bronze_dir, silver_dir = setup_directories

    filename = "olist_geolocation_dataset.csv"

    df = pd.DataFrame({
        "geolocation_zip_code_prefix": [1000, 1000, 2000],
        "geolocation_lat": [10.0, 10.0, 20.0],
        "geolocation_lng": [30.0, 30.0, 40.0],
        "geolocation_city": ["city_a", "city_a", "city_b"],
        "geolocation_state": ["AA", "AA", "BB"],
    })

    df.to_csv(bronze_dir / filename, index=False)

    result = pipeline.transform_to_silver(filename)

    output = pd.read_csv(silver_dir / filename)

    assert len(output) == 2
    assert output.duplicated().sum() == 0
    assert result["exact_duplicates_removed"] == 1


def test_non_positive_payments_are_flagged(setup_directories):
    bronze_dir, silver_dir = setup_directories

    filename = "olist_order_payments_dataset.csv"

    df = pd.DataFrame({
        "order_id": ["order_1", "order_2", "order_3"],
        "payment_sequential": [1, 1, 1],
        "payment_type": ["credit_card", "credit_card", "boleto"],
        "payment_installments": [1, 1, 1],
        "payment_value": [100.0, 0.0, -5.0],
    })

    df.to_csv(bronze_dir / filename, index=False)

    pipeline.transform_to_silver(filename)

    output = pd.read_csv(silver_dir / filename)

    assert output["payment_value_is_positive"].tolist() == [
        True, False, False
    ]
    assert len(output) == 3


def test_invalid_product_weights_are_flagged(setup_directories):
    bronze_dir, silver_dir = setup_directories

    filename = "olist_products_dataset.csv"

    df = pd.DataFrame({
        "product_id": ["p1", "p2", "p3"],
        "product_weight_g": [500.0, 0.0, None],
    })

    df.to_csv(bronze_dir / filename, index=False)

    pipeline.transform_to_silver(filename)

    output = pd.read_csv(silver_dir / filename)

    assert output["product_weight_is_positive"].tolist() == [
        True, False, False
    ]


def test_missing_bronze_file_raises_error(setup_directories):
    with pytest.raises(FileNotFoundError, match="BRONZE file not found"):
        pipeline.transform_to_silver("missing_file.csv")
