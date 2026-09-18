from evaluation.masters_nli.nli_adapter import classification_summary, expected_calibration_error, percentile


def test_ece_perfect_confidence_is_zero():
    assert expected_calibration_error([1.0, 1.0], [True, True]) == 0.0


def test_ece_penalises_confident_error():
    assert expected_calibration_error([1.0], [False]) == 1.0


def test_percentile_interpolates():
    assert percentile([10.0, 20.0, 30.0], 0.5) == 20.0


def test_classification_summary_reports_probabilistic_metrics():
    rows = [
        {"label": "contradiction", "severity": "Critical", "meaning_preserving_control": False},
        {"label": "entailment", "severity": None, "meaning_preserving_control": True},
        {"label": "neutral", "severity": None, "meaning_preserving_control": False},
    ]
    predictions = [
        {
            "label": "contradiction",
            "confidence": 0.90,
            "scores": {"contradiction": 0.90, "entailment": 0.05, "neutral": 0.05},
            "latency_ms": 10.0,
        },
        {
            "label": "entailment",
            "confidence": 0.80,
            "scores": {"contradiction": 0.10, "entailment": 0.80, "neutral": 0.10},
            "latency_ms": 12.0,
        },
        {
            "label": "neutral",
            "confidence": 0.70,
            "scores": {"contradiction": 0.10, "entailment": 0.20, "neutral": 0.70},
            "latency_ms": 11.0,
        },
    ]

    summary = classification_summary(rows, predictions)

    assert summary["accuracy"] == 1.0
    assert summary["brier_score"] >= 0.0
    assert summary["negative_log_likelihood"] >= 0.0
    assert summary["critical_error_recall"] == 1.0
    assert summary["false_positive_rate_controls"] == 0.0
