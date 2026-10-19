
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"


def load_csv(name):
    return pd.read_csv(RAW / name, low_memory=False)


def report_key(df, columns, table):
    print(f"\n{table}: {columns}")
    print("  Null key rows:", int(df[columns].isna().any(axis=1).sum()))
    print("  Duplicate key rows:", int(df.duplicated(columns).sum()))


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
    print("Negative item prices:", int((items["price"] < 0).sum()))
    print("Negative freight values:", int((items["freight_value"] < 0).sum()))
    print("Non-positive payment values:", int((payments["payment_value"] <= 0).sum()))
    print("Review scores outside 1-5:", int((~reviews["review_score"].between(1, 5)).sum()))

    print("\n=== PRODUCT DIMENSIONS ===")
    dimension_columns = [
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]
    for column in dimension_columns:
        print(
            f"{column}: zero={int((products[column] == 0).sum())}, "
            f"negative={int((products[column] < 0).sum())}, "
            f"missing={int(products[column].isna().sum())}"
        )

    print("\n=== GEOLOCATION RANGES ===")
    invalid_lat = ~geo["geolocation_lat"].between(-90, 90)
    invalid_lng = ~geo["geolocation_lng"].between(-180, 180)
    print("Invalid latitude rows:", int(invalid_lat.sum()))
    print("Invalid longitude rows:", int(invalid_lng.sum()))
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
