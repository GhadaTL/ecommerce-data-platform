
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"

CSV_FILES = sorted(RAW_DIR.glob("*.csv"))


def profile_csv(file_path: Path) -> None:
    print("\n" + "=" * 80)
    print(f"FILE: {file_path.name}")
    print("=" * 80)

    df = pd.read_csv(file_path, low_memory=False)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumn names and data types:")
    print(df.dtypes.to_string())

    print("\nMissing values:")
    missing = df.isna().sum()
    missing = missing[missing > 0]

    if missing.empty:
        print("No missing values.")
    else:
        print(missing.to_string())

    print("\nDuplicate complete rows:")
    print(f"{df.duplicated().sum():,}")

    print("\nFirst three rows:")
    print(df.head(3).to_string(index=False))


def main() -> None:
    if not CSV_FILES:
        raise FileNotFoundError(
            f"No CSV files found in {RAW_DIR}. "
            "Download and extract the Olist dataset there."
        )

    print(f"Found {len(CSV_FILES)} CSV files in {RAW_DIR}")

    for file_path in CSV_FILES:
        profile_csv(file_path)


if __name__ == "__main__":
    main()
