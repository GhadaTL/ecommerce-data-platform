
import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORT_PATH = PROJECT_ROOT / "data" / "reports" / "data_quality_report.json"
HISTORY_PATH = PROJECT_ROOT / "data" / "reports" / "quality_metrics_history.csv"


def extract_quality_metrics(report):
    """Extract key quality metrics from the data quality report."""

    checks = report["checks"]

    metrics = {
        "run_timestamp": report["generated_at"],
        "dataset": report["dataset"],
        "total_checks": report["checks_count"],
        "pass_checks": sum(
            check["status"] == "PASS" for check in checks
        ),
        "review_checks": sum(
            check["status"] == "REVIEW" for check in checks
        ),
        "fail_checks": sum(
            check["status"] == "FAIL" for check in checks
        ),
    }

    for check in checks:
        name = check["name"]

        if name == "non_positive_payments":
            metrics["non_positive_payments"] = check.get(
                "invalid_count", 0
            )

        elif name.startswith("product_dimension_"):
            dimension = name.replace(
                "product_dimension_", ""
            )

            metrics[f"{dimension}_zero"] = check.get("zero", 0)
            metrics[f"{dimension}_negative"] = check.get(
                "negative", 0
            )
            metrics[f"{dimension}_missing"] = check.get(
                "missing", 0
            )

        elif name == "key_validation_order_reviews":
            metrics["duplicate_review_ids"] = check.get(
                "duplicates", 0
            )
            metrics["null_review_ids"] = check.get("nulls", 0)

        elif name == "category_translation_coverage":
            metrics["unmatched_categories"] = check.get(
                "unmatched_count", 0
            )

    return metrics


def save_metrics(metrics):
    """Append the current metrics to the historical CSV file."""

    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)

    new_row = pd.DataFrame([metrics])

    if HISTORY_PATH.exists():
        history = pd.read_csv(HISTORY_PATH)
        history = pd.concat(
            [history, new_row],
            ignore_index=True
        )
    else:
        history = new_row

    history.to_csv(HISTORY_PATH, index=False)


def main():
    if not REPORT_PATH.exists():
        raise FileNotFoundError(
            f"Quality report not found: {REPORT_PATH}"
        )

    with open(REPORT_PATH, "r", encoding="utf-8") as file:
        report = json.load(file)

    metrics = extract_quality_metrics(report)
    save_metrics(metrics)

    print("Quality metrics successfully recorded.")
    print(f"History file: {HISTORY_PATH}")
    print(f"Metrics recorded: {len(metrics)}")


if __name__ == "__main__":
    main()
