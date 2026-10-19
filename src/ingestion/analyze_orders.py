
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FILE_PATH = PROJECT_ROOT / "data" / "raw" / "olist_orders_dataset.csv"

df = pd.read_csv(FILE_PATH)

# 1. Distribution des statuts
print("\n=== ORDER STATUS DISTRIBUTION ===")
print(df["order_status"].value_counts(dropna=False))

# 2. Vérification de l'unicité des identifiants
print("\n=== ORDER ID UNIQUENESS ===")
print(f"Total rows: {len(df)}")
print(f"Unique order IDs: {df['order_id'].nunique()}")
print(f"Duplicate order IDs: {df['order_id'].duplicated().sum()}")

# 3. Valeurs manquantes par statut
date_columns = [
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
]

print("\n=== MISSING VALUES BY ORDER STATUS ===")
print(
    df.groupby("order_status")[date_columns]
    .agg(lambda column: column.isna().sum())
    .to_string()
)

# 4. Contrôle des dates après conversion
date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

for column in date_columns:
    df[column] = pd.to_datetime(df[column], errors="coerce")

print("\n=== DATE ORDERING CHECKS ===")

approved_before_purchase = (
    df["order_approved_at"] < df["order_purchase_timestamp"]
).fillna(False)

delivered_before_purchase = (
    df["order_delivered_customer_date"]
    < df["order_purchase_timestamp"]
).fillna(False)

delivered_after_estimate = (
    df["order_delivered_customer_date"]
    > df["order_estimated_delivery_date"]
).fillna(False)

print(
    "Approval before purchase:",
    int(approved_before_purchase.sum()),
)
print(
    "Delivery before purchase:",
    int(delivered_before_purchase.sum()),
)
print(
    "Delivered after estimated date:",
    int(delivered_after_estimate.sum()),
)
