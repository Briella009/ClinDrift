from evaluation.masters_nli.nli_adapter import expected_calibration_error, percentile


def test_ece_perfect_confidence_is_zero():
    assert expected_calibration_error([1.0, 1.0], [True, True]) == 0.0


def test_ece_penalises_confident_error():
    assert expected_calibration_error([1.0], [False]) == 1.0


def test_percentile_interpolates():
    assert percentile([10.0, 20.0, 30.0], 0.5) == 20.0
