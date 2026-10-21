
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"


def load_csv(name):
    return pd.read_csv(RAW / name, low_memory=False)


def count_non_positive_payments(payments):
    return int((payments["payment_value"] <= 0).sum())

def count_invalid_review_scores(reviews):
    valid_scores = reviews["review_score"].between(1, 5)
    return int((~valid_scores).sum())

def report_key(df, columns, table):
    print(f"\n{table}: {columns}")
    print(
        "  Null key rows:",
        int(df[columns].isna().any(axis=1).sum()),
    )
    print(
        "  Duplicate key rows:",
        int(df.duplicated(columns).sum()),
    )

def count_negative_item_prices(items):
    return int((items["price"] < 0).sum())


def count_negative_freight_values(items):
    return int((items["freight_value"] < 0).sum())

def count_invalid_product_dimensions(products, column):
    values = products[column]

    return {
        "zero": int((values == 0).sum()),
        "negative": int((values < 0).sum()),
        "missing": int(values.isna().sum()),
    }


def count_invalid_coordinates(geo):
    invalid_lat = ~geo["geolocation_lat"].between(-90, 90)
    invalid_lng = ~geo["geolocation_lng"].between(-180, 180)

    return {
        "invalid_latitude": int(invalid_lat.sum()),
        "invalid_longitude": int(invalid_lng.sum()),
    }



def main():
    reviews = load_csv("olist_order_reviews_dataset.csv")
    items = load_csv("olist_order_items_dataset.csv")
    payments = load_csv("olist_order_payments_dataset.csv")
    products = load_csv("olist_products_dataset.csv")
    geo = load_csv("olist_geolocation_dataset.csv")

    print("=== REVIEW KEY CANDIDATES ===")
    report_key(reviews, ["review_id"], "reviews")
    report_key(reviews, ["review_id", "order_id"], "reviews")
    report_key(reviews, ["order_id"], "reviews")

    print("\n=== NUMERIC VALUE CHECKS ===")
    print(
    "Negative item prices:",
    count_negative_item_prices(items),
    )
    print(
    "Negative freight values:",
    count_negative_freight_values(items),
    )
    print(
        "Non-positive payment values:",
        count_non_positive_payments(payments),
    )
    print(
    "Review scores outside 1-5:",
    count_invalid_review_scores(reviews),
    )

    print("\n=== PRODUCT DIMENSIONS ===")
    dimension_columns = [
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]

    for column in dimension_columns:
        counts = count_invalid_product_dimensions(products, column)

        print(
            f"{column}: zero={counts['zero']}, "
            f"negative={counts['negative']}, "
            f"missing={counts['missing']}"
        )
    
    print("\n=== GEOLOCATION RANGES ===")

    coordinate_errors = count_invalid_coordinates(geo)

    print(
        "Invalid latitude rows:",
        coordinate_errors["invalid_latitude"],
    )
    print(
        "Invalid longitude rows:",
        coordinate_errors["invalid_longitude"],
    )


    print("\n=== NON-POSITIVE PAYMENTS ===")
    print(
        payments.loc[
            payments["payment_value"] <= 0,
            [
                "order_id",
                "payment_sequential",
                "payment_type",
                "payment_installments",
                "payment_value",
            ],
        ].to_string(index=False)
    )

    print("\n=== ALL PAYMENTS FOR AFFECTED ORDERS ===")

    affected_orders = payments.loc[
        payments["payment_value"] <= 0, "order_id"
    ].unique()

    related_payments = payments[
        payments["order_id"].isin(affected_orders)
    ].sort_values(["order_id", "payment_sequential"])

    print(
        related_payments[
            [
                "order_id",
                "payment_sequential",
                "payment_type",
                "payment_installments",
                "payment_value",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
