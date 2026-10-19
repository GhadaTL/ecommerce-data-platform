
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"


def load_csv(filename):
    return pd.read_csv(RAW / filename, low_memory=False)


def investigate_reviews():
    reviews = load_csv("olist_order_reviews_dataset.csv")

    print("\n=== REVIEW ID INVESTIGATION ===")

    duplicated = reviews[
        reviews.duplicated(subset=["review_id"], keep=False)
    ].sort_values("review_id")

    print("Rows involved in repeated review IDs:", len(duplicated))
    print(
        "Distinct repeated review IDs:",
        duplicated["review_id"].nunique(),
    )

    print("\nFirst repeated review IDs:")
    print(duplicated.head(15).to_string(index=False))

    print("\nRepeated review IDs associated with multiple orders:")
    orders_per_review = reviews.groupby("review_id")["order_id"].nunique()
    print(int((orders_per_review > 1).sum()))

    print("\nRepeated review IDs with different content:")
    content_columns = [
        "order_id",
        "review_score",
        "review_comment_title",
        "review_comment_message",
        "review_creation_date",
        "review_answer_timestamp",
    ]

    content_variations = (
        reviews.groupby("review_id")[content_columns]
        .nunique(dropna=False)
    )

    repeated_ids = reviews["review_id"].value_counts()
    repeated_ids = repeated_ids[repeated_ids > 1].index

    variations = content_variations.loc[repeated_ids]
    print(int(variations.gt(1).any(axis=1).sum()))


def investigate_categories():
    products = load_csv("olist_products_dataset.csv")
    translations = load_csv("product_category_name_translation.csv")

    print("\n=== PRODUCT CATEGORY INVESTIGATION ===")

    product_categories = set(
        products["product_category_name"].dropna().unique()
    )
    translated_categories = set(
        translations["product_category_name"].dropna().unique()
    )

    missing_translations = sorted(
        product_categories - translated_categories
    )

    print("Categories without English translation:")
    for category in missing_translations:
        count = (
            products["product_category_name"] == category
        ).sum()
        print(f"- {category}: {count} products")

    print("\nProducts without a category:")
    print(int(products["product_category_name"].isna().sum()))


if __name__ == "__main__":
    investigate_reviews()
    investigate_categories()
