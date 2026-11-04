
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

HISTORY_PATH = (
    PROJECT_ROOT
    / "data"
    / "reports"
    / "quality_metrics_history.csv"
)


# Metrics for which an increase may indicate data quality degradation.
BAD_COUNT_METRICS = [
    "non_positive_payments",
    "product_weight_g_zero",
    "product_weight_g_negative",
    "product_weight_g_missing",
    "product_length_cm_zero",
    "product_length_cm_negative",
    "product_length_cm_missing",
    "product_height_cm_zero",
    "product_height_cm_negative",
    "product_height_cm_missing",
    "product_width_cm_zero",
    "product_width_cm_negative",
    "product_width_cm_missing",
    "null_review_ids",
    "unmatched_categories",
]

# An increase in these metrics deserves attention,
# but does not automatically mean that the data is invalid.
INFORMATIONAL_METRICS = [
    "duplicate_review_ids",
]


def detect_anomalies(previous_run, current_run):
    """Compare two runs and detect potential quality degradation."""

    anomalies = []

    for metric in BAD_COUNT_METRICS:
        if metric not in previous_run.index or metric not in current_run.index:
            continue

        previous_value = previous_run[metric]
        current_value = current_run[metric]

        if pd.isna(previous_value) or pd.isna(current_value):
            continue

        previous_value = float(previous_value)
        current_value = float(current_value)

        if current_value > previous_value:
            anomalies.append({
                "metric": metric,
                "previous_value": previous_value,
                "current_value": current_value,
                "change": current_value - previous_value,
                "severity": "WARNING",
            })

    # An increase in failed checks is critical.
    previous_fails = float(previous_run["fail_checks"])
    current_fails = float(current_run["fail_checks"])

    if current_fails > previous_fails:
        anomalies.append({
            "metric": "fail_checks",
            "previous_value": previous_fails,
            "current_value": current_fails,
            "change": current_fails - previous_fails,
            "severity": "CRITICAL",
        })

    # An increase in checks requiring review deserves attention.
    previous_reviews = float(previous_run["review_checks"])
    current_reviews = float(current_run["review_checks"])

    if current_reviews > previous_reviews:
        anomalies.append({
            "metric": "review_checks",
            "previous_value": previous_reviews,
            "current_value": current_reviews,
            "change": current_reviews - previous_reviews,
            "severity": "WARNING",
        })

    # A decrease in passed checks may indicate degradation.
    previous_passes = float(previous_run["pass_checks"])
    current_passes = float(current_run["pass_checks"])

    if current_passes < previous_passes:
        anomalies.append({
            "metric": "pass_checks",
            "previous_value": previous_passes,
            "current_value": current_passes,
            "change": current_passes - previous_passes,
            "severity": "WARNING",
        })

    # Track review_id duplicates as informational, not as an error.
    for metric in INFORMATIONAL_METRICS:
        if metric not in previous_run.index or metric not in current_run.index:
            continue

        previous_value = float(previous_run[metric])
        current_value = float(current_run[metric])

        if current_value > previous_value:
            anomalies.append({
                "metric": metric,
                "previous_value": previous_value,
                "current_value": current_value,
                "change": current_value - previous_value,
                "severity": "INFO",
            })

    return anomalies


def main():
    if not HISTORY_PATH.exists():
        raise FileNotFoundError(
            f"History file not found: {HISTORY_PATH}"
        )

    history = pd.read_csv(HISTORY_PATH)

    if len(history) < 2:
        print("Not enough historical runs for anomaly detection.")
        print("At least two different runs are required.")
        return

    previous_run = history.iloc[-2]
    current_run = history.iloc[-1]

    print("Previous run:", previous_run["run_timestamp"])
    print("Current run:", current_run["run_timestamp"])
    print("-" * 60)

    anomalies = detect_anomalies(previous_run, current_run)

    if not anomalies:
        print("No quality degradation detected.")
        return

    print(f"{len(anomalies)} potential anomaly/anomalies detected:\n")

    for anomaly in anomalies:
        print(f"[{anomaly['severity']}] {anomaly['metric']}")
        print(
            f"  Previous: {anomaly['previous_value']} "
            f"-> Current: {anomaly['current_value']}"
        )
        print(f"  Change: {anomaly['change']}")
        print()


if __name__ == "__main__":
    main()
