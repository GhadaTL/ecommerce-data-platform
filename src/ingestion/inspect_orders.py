
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ORDERS_FILE = PROJECT_ROOT / "data" / "raw" / "olist_orders_dataset.csv"


def main() -> None:
    if not ORDERS_FILE.exists():
        raise FileNotFoundError(
            f"Orders dataset not found: {ORDERS_FILE}\n"
            "Download the Olist dataset and place the CSV in data/raw/."
        )

    orders = pd.read_csv(ORDERS_FILE)

    print("\n--- Dataset shape ---")
    print(f"Rows: {len(orders):,}")
    print(f"Columns: {len(orders.columns)}")

    print("\n--- Column names ---")
    print(orders.columns.tolist())

    print("\n--- First five rows ---")
    print(orders.head())

    print("\n--- Data types ---")
    print(orders.dtypes)

    print("\n--- Missing values ---")
    print(orders.isna().sum())

    print("\n--- Duplicate order IDs ---")
    print(orders["order_id"].duplicated().sum())


if __name__ == "__main__":
    main()
