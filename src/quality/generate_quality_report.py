
"""
Generate a structured JSON report for Olist data quality checks.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from src.quality.validate_data_quality import (
    load_csv as load_quality_csv,
    count_non_positive_payments,
    count_invalid_review_scores,
    count_negative_item_prices,
    count_negative_freight_values,
    count_invalid_product_dimensions,
    count_invalid_coordinates,
)

from src.quality.validate_relationships import (
    load_csv as load_relationship_csv,
    check_unique,
    check_foreign_key,
    check_category_translation,
)


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "data" / "reports"


def generate_quality_report():
    """Run quality checks and save their results as JSON."""
    # Load datasets used by the quality checks.
    payments = load_quality_csv("olist_order_payments_dataset.csv")
    reviews = load_quality_csv("olist_order_reviews_dataset.csv")
    items = load_quality_csv("olist_order_items_dataset.csv")
    products = load_quality_csv("olist_products_dataset.csv")
    geo = load_quality_csv("olist_geolocation_dataset.csv")

    # Load datasets used by the relationship checks.
    orders = load_relationship_csv("olist_orders_dataset.csv")
    customers = load_relationship_csv("olist_customers_dataset.csv")
    relationship_items = load_relationship_csv(
        "olist_order_items_dataset.csv"
    )
    relationship_payments = load_relationship_csv(
        "olist_order_payments_dataset.csv"
    )
    relationship_reviews = load_relationship_csv(
        "olist_order_reviews_dataset.csv"
    )
    relationship_products = load_relationship_csv(
        "olist_products_dataset.csv"
    )
    sellers = load_relationship_csv("olist_sellers_dataset.csv")
    translations = load_relationship_csv(
        "product_category_name_translation.csv"
    )

    checks = []

    # Numeric and dimensional quality checks.
    checks.append({
        "name": "non_positive_payments",
        "category": "data_quality",
        "invalid_count": count_non_positive_payments(payments),
    })

    checks.append({
        "name": "invalid_review_scores",
        "category": "data_quality",
        "invalid_count": count_invalid_review_scores(reviews),
    })

    checks.append({
        "name": "negative_item_prices",
        "category": "data_quality",
        "invalid_count": count_negative_item_prices(items),
    })

    checks.append({
        "name": "negative_freight_values",
        "category": "data_quality",
        "invalid_count": count_negative_freight_values(items),
    })

    for column in [
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]:
        result = count_invalid_product_dimensions(products, column)

        checks.append({
            "name": f"product_dimension_{column}",
            "category": "data_quality",
            **result,
        })

    checks.append({
        "name": "invalid_geographic_coordinates",
        "category": "data_quality",
        **count_invalid_coordinates(geo),
    })

    # Primary and candidate key checks.
    key_checks = [
        (orders, ["order_id"], "orders"),
        (customers, ["customer_id"], "customers"),
        (relationship_products, ["product_id"], "products"),
        (sellers, ["seller_id"], "sellers"),
        (
            relationship_items,
            ["order_id", "order_item_id"],
            "order_items",
        ),
        (
            relationship_payments,
            ["order_id", "payment_sequential"],
            "order_payments",
        ),
        (relationship_reviews, ["review_id"], "order_reviews"),
        (
            translations,
            ["product_category_name"],
            "category_translation",
        ),
    ]

    for df, columns, table in key_checks:
        result = check_unique(df, columns, table)
        checks.append({
            "name": f"key_validation_{table}",
            "category": "key_integrity",
            **result,
        })

    # Foreign key checks.
    foreign_key_checks = [
        (
            orders, "customer_id", customers, "customer_id",
            "orders_customer",
        ),
        (
            relationship_items, "order_id", orders, "order_id",
            "items_order",
        ),
        (
            relationship_items, "product_id",
            relationship_products, "product_id",
            "items_product",
        ),
        (
            relationship_items, "seller_id", sellers, "seller_id",
            "items_seller",
        ),
        (
            relationship_payments, "order_id", orders, "order_id",
            "payments_order",
        ),
        (
            relationship_reviews, "order_id", orders, "order_id",
            "reviews_order",
        ),
    ]

    for child, child_col, parent, parent_col, label in foreign_key_checks:
        result = check_foreign_key(
            child,
            child_col,
            parent,
            parent_col,
            label,
        )
        checks.append({
            "name": f"foreign_key_{label}",
            "category": "foreign_key_integrity",
            **result,
        })

    # Category translation coverage.
    translation_result = check_category_translation(
        relationship_products,
        translations,
    )
    checks.append({
        "name": "category_translation_coverage",
        "category": "reference_data",
        **translation_result,
    })

    # Add a simple status to every check.
    
    for check in checks:
        if "invalid_count" in check:
            check["status"] = (
                "PASS" if check["invalid_count"] == 0 else "REVIEW"
            )

        elif "zero" in check and "negative" in check and "missing" in check:
            has_invalid_values = (
                check["zero"] > 0
                or check["negative"] > 0
                or check["missing"] > 0
            )
            check["status"] = "REVIEW" if has_invalid_values else "PASS"

        elif "invalid_latitude" in check and "invalid_longitude" in check:
            has_invalid_coordinates = (
                check["invalid_latitude"] > 0
                or check["invalid_longitude"] > 0
            )
            check["status"] = (
                "REVIEW" if has_invalid_coordinates else "PASS"
            )

        elif "duplicates" in check and "nulls" in check:
            check["status"] = (
                "PASS"
                if check["duplicates"] == 0 and check["nulls"] == 0
                else "REVIEW"
            )

        elif "missing_parent_values" in check:
            check["status"] = (
                "PASS"
                if check["missing_parent_values"] == 0
                else "FAIL"
            )

        elif "unmatched_count" in check:
            check["status"] = (
                "PASS" if check["unmatched_count"] == 0 else "REVIEW"
            )

    report = {
        "dataset": "olist",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "checks_count": len(checks),
        "checks": checks,
    }

    REPORTS.mkdir(parents=True, exist_ok=True)
    output_path = REPORTS / "data_quality_report.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    print(f"\nQuality report saved to: {output_path}")
    print(f"Total checks: {len(checks)}")
    print(
        "Checks requiring review:",
        sum(check["status"] == "REVIEW" for check in checks),
    )
    print(
        "Failed checks:",
        sum(check["status"] == "FAIL" for check in checks),
    )


if __name__ == "__main__":
    generate_quality_report()
