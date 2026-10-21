
import pandas as pd
from src.quality.validate_data_quality import count_non_positive_payments
from src.quality.validate_data_quality import count_invalid_review_scores
from src.quality.validate_data_quality import (
    count_negative_item_prices,
    count_negative_freight_values,
)

from src.quality.validate_data_quality import (
    count_invalid_product_dimensions,
)

from src.quality.validate_data_quality import count_invalid_coordinates

def test_primary_key_is_unique():
    orders = pd.DataFrame({
        "order_id": ["o1", "o2", "o3"],
    })

    assert orders["order_id"].is_unique


def test_duplicate_primary_key_is_detected():
    orders = pd.DataFrame({
        "order_id": ["o1", "o2", "o1"],
    })

    assert not orders["order_id"].is_unique
    assert orders["order_id"].duplicated().sum() == 1


def test_foreign_keys_have_matching_parents():
    customers = pd.DataFrame({
        "customer_id": ["c1", "c2"],
    })
    orders = pd.DataFrame({
        "customer_id": ["c1", "c2", "c1"],
    })

    parent_ids = set(customers["customer_id"])
    unmatched = ~orders["customer_id"].isin(parent_ids)

    assert unmatched.sum() == 0


def test_missing_foreign_key_parent_is_detected():
    customers = pd.DataFrame({
        "customer_id": ["c1", "c2"],
    })
    orders = pd.DataFrame({
        "customer_id": ["c1", "c3"],
    })

    parent_ids = set(customers["customer_id"])
    unmatched = ~orders["customer_id"].isin(parent_ids)

    assert unmatched.sum() == 1


def test_review_scores_are_between_one_and_five():
    reviews = pd.DataFrame({
        "review_score": [1, 3, 5],
    })

    assert reviews["review_score"].between(1, 5).all()


def test_invalid_review_scores_are_detected():
    reviews = pd.DataFrame({
        "review_score": [1, 3, 6],
    })

    valid_scores = reviews["review_score"].between(1, 5)

    assert (~valid_scores).sum() == 1


def test_count_non_positive_payments():
    payments = pd.DataFrame({
        "payment_value": [25.0, 0.0, 12.0, -5.0],
    })

    assert count_non_positive_payments(payments) == 2
 

def test_count_invalid_review_scores():
    reviews = pd.DataFrame({
        "review_score": [1, 3, 5, 0, 6],
    })

    assert count_invalid_review_scores(reviews) == 2

def test_count_negative_item_prices():
    items = pd.DataFrame({
        "price": [100.0, 25.0, -5.0, 0.0],
    })

    assert count_negative_item_prices(items) == 1


def test_count_negative_freight_values():
    items = pd.DataFrame({
        "freight_value": [10.0, 0.0, -2.0, 5.0],
    })

    assert count_negative_freight_values(items) == 1

def test_count_invalid_product_dimensions():
    products = pd.DataFrame({
        "product_weight_g": [100, 0, -5, None, 250],
    })

    result = count_invalid_product_dimensions(
        products,
        "product_weight_g",
    )

    assert result == {
        "zero": 1,
        "negative": 1,
        "missing": 1,
    }

    
def test_count_invalid_coordinates():
    geo = pd.DataFrame({
        "geolocation_lat": [36.8, 91.0, -90.0],
        "geolocation_lng": [10.2, 181.0, -180.0],
    })

    result = count_invalid_coordinates(geo)

    assert result == {
        "invalid_latitude": 1,
        "invalid_longitude": 1,
    }
