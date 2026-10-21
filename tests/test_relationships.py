
import pandas as pd

from src.quality.validate_relationships import (
    check_foreign_key,
    check_unique,
)


def test_check_unique_with_valid_keys(capsys):
    df = pd.DataFrame({
        "order_id": ["o1", "o2", "o3"],
    })

    result = check_unique(df, ["order_id"], "orders")

    assert result["duplicates"] == 0
    assert result["nulls"] == 0


def test_check_unique_detects_duplicates_and_nulls(capsys):
    df = pd.DataFrame({
        "order_id": ["o1", "o2", "o1", None],
    })

    result = check_unique(df, ["order_id"], "orders")

    assert result["duplicates"] == 1
    assert result["nulls"] == 1


def test_check_unique_with_composite_key():
    df = pd.DataFrame({
        "order_id": ["o1", "o1", "o2"],
        "order_item_id": [1, 2, 1],
    })

    result = check_unique(
        df,
        ["order_id", "order_item_id"],
        "order_items",
    )

    assert result["duplicates"] == 0
    assert result["nulls"] == 0


def test_check_foreign_key_with_matching_parents():
    child = pd.DataFrame({
        "customer_id": ["c1", "c2", "c1"],
    })
    parent = pd.DataFrame({
        "customer_id": ["c1", "c2", "c3"],
    })

    result = check_foreign_key(
        child,
        "customer_id",
        parent,
        "customer_id",
        "orders.customer_id -> customers.customer_id",
    )

    assert result["distinct_child_values"] == 2
    assert result["missing_parent_values"] == 0


def test_check_foreign_key_detects_missing_parent():
    child = pd.DataFrame({
        "customer_id": ["c1", "c2", "c_missing"],
    })
    parent = pd.DataFrame({
        "customer_id": ["c1", "c2"],
    })

    result = check_foreign_key(
        child,
        "customer_id",
        parent,
        "customer_id",
        "orders.customer_id -> customers.customer_id",
    )

    assert result["distinct_child_values"] == 3
    assert result["missing_parent_values"] == 1
