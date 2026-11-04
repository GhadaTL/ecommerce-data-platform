
import pandas as pd

from src.observability.detect_quality_anomalies import (
    detect_anomalies,
)


def create_run(
    non_positive_payments=9,
    unmatched_categories=2,
    fail_checks=0,
    review_checks=7,
    pass_checks=17,
    duplicate_review_ids=814,
):
    """Create artificial run metrics for testing."""

    return pd.Series({
        "non_positive_payments": non_positive_payments,
        "unmatched_categories": unmatched_categories,
        "fail_checks": fail_checks,
        "review_checks": review_checks,
        "pass_checks": pass_checks,
        "duplicate_review_ids": duplicate_review_ids,
    })


def test_no_anomalies_when_metrics_are_stable():
    previous_run = create_run()
    current_run = create_run()

    anomalies = detect_anomalies(previous_run, current_run)

    assert anomalies == []


def test_detect_increase_in_non_positive_payments():
    previous_run = create_run(non_positive_payments=9)
    current_run = create_run(non_positive_payments=15)

    anomalies = detect_anomalies(previous_run, current_run)

    assert any(
        anomaly["metric"] == "non_positive_payments"
        and anomaly["severity"] == "WARNING"
        and anomaly["change"] == 6
        for anomaly in anomalies
    )


def test_detect_increase_in_unmatched_categories():
    previous_run = create_run(unmatched_categories=2)
    current_run = create_run(unmatched_categories=5)

    anomalies = detect_anomalies(previous_run, current_run)

    assert any(
        anomaly["metric"] == "unmatched_categories"
        and anomaly["change"] == 3
        for anomaly in anomalies
    )


def test_detect_new_failed_checks():
    previous_run = create_run(fail_checks=0)
    current_run = create_run(fail_checks=1)

    anomalies = detect_anomalies(previous_run, current_run)

    assert any(
        anomaly["metric"] == "fail_checks"
        and anomaly["severity"] == "CRITICAL"
        for anomaly in anomalies
    )


def test_duplicate_review_ids_are_informational():
    previous_run = create_run(duplicate_review_ids=814)
    current_run = create_run(duplicate_review_ids=820)

    anomalies = detect_anomalies(previous_run, current_run)

    assert any(
        anomaly["metric"] == "duplicate_review_ids"
        and anomaly["severity"] == "INFO"
        for anomaly in anomalies
    )
