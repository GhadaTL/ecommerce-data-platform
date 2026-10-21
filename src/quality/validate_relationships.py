
"""
Validate primary/candidate keys, foreign keys, and category translations
in the Olist dataset.
"""

from pathlib import Path

import pandas as pd


# -------------------------------------------------------------------
# Paths and data loading
# -------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"


def load_csv(name):
    """Load a CSV file from the raw data directory."""
    return pd.read_csv(RAW / name, low_memory=False)


# -------------------------------------------------------------------
# Primary and candidate key validation
# -------------------------------------------------------------------

def check_unique(df, columns, table):
    """
    Check duplicate and null rows for a candidate key.

    Args:
        df: DataFrame to validate.
        columns: Column name or list of columns forming the key.
        table: Table name displayed in the report.

    Returns:
        Dictionary containing duplicate and null row counts.
    """
    duplicates = int(df.duplicated(subset=columns).sum())
    nulls = int(df[columns].isna().any(axis=1).sum())

    print(
        f"{table}: key={columns}, "
        f"duplicate keys={duplicates:,}, "
        f"rows with null key={nulls:,}"
    )

    return {
        "table": table,
        "columns": columns,
        "duplicates": duplicates,
        "nulls": nulls,
    }


# -------------------------------------------------------------------
# Foreign key validation
# -------------------------------------------------------------------

def check_foreign_key(child, child_col, parent, parent_col, label):
    """
    Check whether distinct, non-null child values exist in the parent.

    Returns:
        Dictionary containing distinct child values and missing parents.
    """
    child_values = child[child_col].dropna().unique()
    parent_values = set(parent[parent_col].dropna().unique())

    missing_values = [
        value
        for value in child_values
        if value not in parent_values
    ]

    print(
        f"{label}: distinct child values={len(child_values):,}, "
        f"values without parent={len(missing_values):,}"
    )

    return {
        "label": label,
        "distinct_child_values": len(child_values),
        "missing_parent_values": len(missing_values),
    }


# -------------------------------------------------------------------
# Product category translation validation
# -------------------------------------------------------------------

def check_category_translation(products, translations):
    """
    Check which non-null product categories lack an English translation.

    Returns:
        Dictionary containing category counts and unmatched categories.
    """
    product_categories = set(
        products["product_category_name"].dropna().unique()
    )
    translated_categories = set(
        translations["product_category_name"].dropna().unique()
    )

    unmatched = sorted(product_categories - translated_categories)

    print("\n=== CATEGORY TRANSLATION COVERAGE ===")
    print(
        "Distinct non-null product categories:",
        len(product_categories),
    )
    print("Categories without translation:", len(unmatched))
    print(unmatched)

    return {
        "distinct_product_categories": len(product_categories),
        "unmatched_categories": unmatched,
        "unmatched_count": len(unmatched),
    }


# -------------------------------------------------------------------
# Main relationship report
# -------------------------------------------------------------------

def main():
    """Load Olist CSV files and run relationship checks."""
    orders = load_csv("olist_orders_dataset.csv")
    customers = load_csv("olist_customers_dataset.csv")
    items = load_csv("olist_order_items_dataset.csv")
    payments = load_csv("olist_order_payments_dataset.csv")
    reviews = load_csv("olist_order_reviews_dataset.csv")
    products = load_csv("olist_products_dataset.csv")
    sellers = load_csv("olist_sellers_dataset.csv")
    translations = load_csv("product_category_name_translation.csv")

    print("\n=== PRIMARY / CANDIDATE KEYS ===")

    check_unique(orders, ["order_id"], "orders")
    check_unique(customers, ["customer_id"], "customers")
    check_unique(products, ["product_id"], "products")
    check_unique(sellers, ["seller_id"], "sellers")

    check_unique(
        items,
        ["order_id", "order_item_id"],
        "order_items",
    )

    check_unique(
        payments,
        ["order_id", "payment_sequential"],
        "order_payments",
    )

    check_unique(
        reviews,
        ["review_id"],
        "order_reviews",
    )

    check_unique(
        translations,
        ["product_category_name"],
        "category_translation",
    )

    print("\n=== FOREIGN KEY CHECKS ===")

    check_foreign_key(
        orders,
        "customer_id",
        customers,
        "customer_id",
        "orders.customer_id -> customers.customer_id",
    )

    check_foreign_key(
        items,
        "order_id",
        orders,
        "order_id",
        "order_items.order_id -> orders.order_id",
    )

    check_foreign_key(
        items,
        "product_id",
        products,
        "product_id",
        "order_items.product_id -> products.product_id",
    )

    check_foreign_key(
        items,
        "seller_id",
        sellers,
        "seller_id",
        "order_items.seller_id -> sellers.seller_id",
    )

    check_foreign_key(
        payments,
        "order_id",
        orders,
        "order_id",
        "order_payments.order_id -> orders.order_id",
    )

    check_foreign_key(
        reviews,
        "order_id",
        orders,
        "order_id",
        "order_reviews.order_id -> orders.order_id",
    )

    check_category_translation(products, translations)


if __name__ == "__main__":
    main()
