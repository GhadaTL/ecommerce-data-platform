
from pathlib import Path
import shutil #for file operations :servira à copier les fichiers de RAW vers BRONZE.
import json #servira à enregistrer le rapport d’exécution.
import pandas as pd


# Racine du projet : ecommerce-data-platform/
ROOT = Path(__file__).resolve().parents[2]

# Dossiers de données
RAW_DIR = ROOT / "data" / "raw"
BRONZE_DIR = ROOT / "data" / "bronze"
SILVER_DIR = ROOT / "data" / "silver"
REPORT_DIR = ROOT / "data" / "reports"


CSV_FILES = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv"
] #declaration de la liste des fichiers CSV à traiter.


DATE_COLUMNS = {
    "olist_orders_dataset.csv": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "olist_order_items_dataset.csv": [
        "shipping_limit_date",
    ],
    "olist_order_reviews_dataset.csv": [
        "review_creation_date",
        "review_answer_timestamp",
    ],
}


def create_directories():
    """Create the directories required by the pipeline."""
    for directory in [BRONZE_DIR, SILVER_DIR, REPORT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    print("Required directories are ready.")


def copy_to_bronze():
    """Copy source CSV files from RAW to BRONZE."""
    copied_files = []

    for filename in CSV_FILES:
        source = RAW_DIR / filename
        destination = BRONZE_DIR / filename

        if not source.exists():
            raise FileNotFoundError(
                f"Source file not found: {source}"
            )

        shutil.copy2(source, destination)
        copied_files.append(filename)

        print(f"Copied: {filename}")

    print(f"\nTotal files copied to BRONZE: {len(copied_files)}")

    return copied_files


def transform_to_silver(filename):
    """Transform one BRONZE CSV file and save it to SILVER."""
    source = BRONZE_DIR / filename
    destination = SILVER_DIR / filename

    if not source.exists():
        raise FileNotFoundError(
            f"BRONZE file not found: {source}"
        )

    df = pd.read_csv(source, low_memory=False)

    print(f"\nProcessing: {filename}")
    print(f"Rows before transformation: {len(df)}")

    invalid_dates = {}
    exact_duplicates_removed = 0

    for column in DATE_COLUMNS.get(filename, []):
        original_values = df[column].notna()

        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

        invalid_count = int(
            (original_values & df[column].isna()).sum()
        )

        invalid_dates[column] = invalid_count

        print(
            f"  {column}: "
            f"{invalid_count} invalid date conversions"
        )

    
    if filename == "olist_geolocation_dataset.csv":
        rows_before_deduplication = len(df)

        df = df.drop_duplicates()

        exact_duplicates_removed = (
            rows_before_deduplication - len(df)
        )

        print(
            "  Exact duplicate rows removed: "
            f"{exact_duplicates_removed}"
        )

        
    if filename == "olist_order_payments_dataset.csv":
        df["payment_value_is_positive"] = (
            df["payment_value"] > 0
        )

        non_positive_count = int(
            (~df["payment_value_is_positive"]).sum()
        )

        print(
            f"  Non-positive payment rows: {non_positive_count}"
        )

    if filename == "olist_products_dataset.csv":
        df["product_weight_is_positive"] = (
            df["product_weight_g"].notna()
            & (df["product_weight_g"] > 0)
        )

        non_positive_weight_count = int(
            (~df["product_weight_is_positive"]).sum()
        )

        print(
            "  Missing or non-positive product weights: "
            f"{non_positive_weight_count}"
        )


    df.to_csv(destination, index=False)

    print(f"Saved to: {destination}")

    return {
    "file": filename,
    "rows": len(df),
    "columns": len(df.columns),
    "exact_duplicates_removed": exact_duplicates_removed,
    "invalid_dates": invalid_dates,
    }


def save_report(results):
    """Save pipeline execution statistics as a JSON report."""
    report = {
        "pipeline": "bronze_to_silver",
        "files_processed": len(results),
        "results": results,
    }

    report_path = REPORT_DIR / "bronze_to_silver_report.json"

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, ensure_ascii=False)

    print(f"\nReport saved to: {report_path}")



if __name__ == "__main__":
    create_directories()
    copy_to_bronze()

    results = []

    for filename in CSV_FILES:
        result = transform_to_silver(filename)
        results.append(result)

    save_report(results)

    print("\nAll files have been processed.")
    print(f"Total files processed: {len(results)}")


