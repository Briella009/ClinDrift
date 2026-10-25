import pytest

from src.safety_metrics import (
    catastrophic_miss_rate,
    critical_error_recall,
    repeated_run_stability,
    review_burden,
)


def test_critical_error_metrics_expose_catastrophic_miss():
    rows = [
        {"severity": "Critical", "flagged": True},
        {"severity": "Critical", "flagged": False},
        {"severity": "High", "flagged": False},
    ]
    assert critical_error_recall(rows) == 0.5
    assert catastrophic_miss_rate(rows) == 0.5


def test_review_burden_reports_escalated_share():
    rows = [
        {"requires_review": True},
        {"requires_review": False},
        {"requires_review": True},
        {"requires_review": False},
    ]
    assert review_burden(rows) == 0.5


def test_repeated_run_stability_uses_finding_signatures():
    finding = {
        "drift_type": "Dosage drift",
        "category": "dosage",
        "source_value": "500 mg",
        "transformed_value": "1000 mg",
    }
    other = {**finding, "transformed_value": "750 mg"}
    assert repeated_run_stability([[finding], [finding]]) == 1.0
    assert repeated_run_stability([[finding], [other]]) == 0.0


def test_repeated_run_stability_requires_replication():
    with pytest.raises(ValueError):
        repeated_run_stability([[]])
