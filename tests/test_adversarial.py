"""
Adversarial evaluation suite for ClinDrift v0.2.

Purpose
-------
This suite tests whether ClinDrift generalises beyond the baseline cases
already covered in tests/test_core.py.

The emphasis is on:
- semantic equivalence
- false-positive resistance
- omission detection
- unsupported additions
- dosage drift
- frequency drift
- duration equivalence
- laterality changes
- allergy contradiction
- measurement drift
- multi-fact records

These tests are intentionally stricter than the baseline suite.
"""

from src.extractor import extract_facts
from src.drift_engine import compare_facts


def _findings(source: str, transformed: str):
    return compare_facts(
        extract_facts(source),
        extract_facts(transformed),
    )


def _types(findings):
    return [f.drift_type for f in findings]


def _critical(findings):
    return [f for f in findings if f.severity == "Critical"]


def _high(findings):
    return [f for f in findings if f.severity == "High"]


# ---------------------------------------------------------------------------
# 1. Exact preservation controls
# ---------------------------------------------------------------------------

def test_exact_record_preserved():
    source = (
        "Patient takes metformin 500 mg twice a day. "
        "Patient is allergic to penicillin. "
        "Blood pressure is 122/78."
    )

    transformed = (
        "Patient takes metformin 500 mg twice a day. "
        "Patient is allergic to penicillin. "
        "Blood pressure is 122/78."
    )

    assert _findings(source, transformed) == []


def test_spacing_only_changes_not_flagged():
    source = "Patient takes metformin 500 mg twice a day. Blood pressure is 122 / 78."
    transformed = "Patient takes metformin 500mg twice a day. Blood pressure is 122/78."

    assert _findings(source, transformed) == []


# ---------------------------------------------------------------------------
# 2. Semantic frequency equivalence
# ---------------------------------------------------------------------------

def test_twice_daily_equivalence():
    source = "Patient takes metformin 500 mg twice a day."
    transformed = "Patient takes metformin 500 mg twice daily."

    assert _findings(source, transformed) == []


def test_two_times_daily_equivalence():
    source = "Patient takes metformin 500 mg twice a day."
    transformed = "Patient takes metformin 500 mg two times daily."

    assert _findings(source, transformed) == []


def test_once_daily_equivalence():
    source = "Patient takes amlodipine 5 mg once a day."
    transformed = "Patient takes amlodipine 5 mg daily."

    assert _findings(source, transformed) == []


def test_true_frequency_change_detected():
    source = "Patient takes metformin 500 mg twice a day."
    transformed = "Patient takes metformin 500 mg once a day."

    findings = _findings(source, transformed)

    assert any(f.drift_type == "Frequency drift" for f in findings)


# ---------------------------------------------------------------------------
# 3. Duration equivalence
# ---------------------------------------------------------------------------

def test_one_week_equals_seven_days():
    source = "Symptoms have persisted for 7 days."
    transformed = "Symptoms have persisted for one week."

    assert _findings(source, transformed) == []


def test_two_weeks_equals_fourteen_days():
    source = "Symptoms have persisted for 14 days."
    transformed = "Symptoms have persisted for two weeks."

    assert _findings(source, transformed) == []


def test_true_duration_change_detected():
    source = "Symptoms have persisted for 3 days."
    transformed = "Symptoms have persisted for 7 days."

    findings = _findings(source, transformed)

    assert any(f.drift_type == "Duration drift" for f in findings)


# ---------------------------------------------------------------------------
# 4. Dosage representation and dosage drift
# ---------------------------------------------------------------------------

def test_dosage_spacing_equivalence():
    source = "Patient takes metformin 500 mg twice a day."
    transformed = "Patient takes metformin 500mg twice a day."

    assert _findings(source, transformed) == []


def test_gram_milligram_equivalence():
    source = "Patient takes paracetamol 1 g once a day."
    transformed = "Patient takes paracetamol 1000 mg once a day."

    assert _findings(source, transformed) == []


def test_microgram_milligram_equivalence():
    source = "Patient takes medication 500 mcg once a day."
    transformed = "Patient takes medication 0.5 mg once a day."

    findings = _findings(source, transformed)

    dosage_findings = [
        f for f in findings
        if f.drift_type == "Dosage drift"
    ]

    assert dosage_findings == []


def test_real_dosage_change_detected():
    source = "Patient takes metformin 500 mg twice a day."
    transformed = "Patient takes metformin 1000 mg twice a day."

    findings = _findings(source, transformed)

    assert any(
        f.drift_type == "Dosage drift"
        and f.severity == "Critical"
        for f in findings
    )


# ---------------------------------------------------------------------------
# 5. Allergy safety cases
# ---------------------------------------------------------------------------

def test_allergy_preserved():
    source = "Patient is allergic to penicillin."
    transformed = "Patient is allergic to penicillin."

    assert _findings(source, transformed) == []


def test_allergy_omission_detected():
    source = "Patient is allergic to penicillin."
    transformed = "Patient reports headaches for 3 days."

    findings = _findings(source, transformed)

    assert any(
        f.drift_type == "Omission"
        and f.severity == "Critical"
        for f in findings
    )


def test_allergy_to_no_known_allergies_is_critical():
    source = "Patient is allergic to penicillin."
    transformed = "Patient has no known drug allergies."

    findings = _findings(source, transformed)

    assert any(
        f.drift_type == "Allergy contradiction"
        and f.severity == "Critical"
        for f in findings
    )


def test_no_known_allergies_to_allergy_is_critical():
    source = "Patient has no known drug allergies."
    transformed = "Patient is allergic to penicillin."

    findings = _findings(source, transformed)

    assert any(
        f.drift_type == "Allergy contradiction"
        and f.severity == "Critical"
        for f in findings
    )


# ---------------------------------------------------------------------------
# 6. Medication omission and unsupported addition
# ---------------------------------------------------------------------------

def test_medication_omission_detected():
    source = "Patient takes metformin 500 mg twice a day."
    transformed = "Patient reports headaches for 3 days."

    findings = _findings(source, transformed)

    assert any(
        f.drift_type == "Omission"
        and f.source_value == "metformin"
        for f in findings
    )


def test_unsupported_medication_addition_detected():
    source = "Patient reports headaches for 3 days."
    transformed = "Patient reports headaches for 3 days and takes warfarin."

    findings = _findings(source, transformed)

    assert any(
        f.drift_type == "Unsupported addition"
        and f.transformed_value == "warfarin"
        for f in findings
    )


def test_multiple_medications_preserved():
    source = "Patient takes metformin and amlodipine."
    transformed = "Patient takes amlodipine and metformin."

    findings = _findings(source, transformed)

    medication_findings = [
        f for f in findings
        if f.source_value in {"metformin", "amlodipine"}
        or f.transformed_value in {"metformin", "amlodipine"}
    ]

    assert medication_findings == []


# ---------------------------------------------------------------------------
# 7. Laterality
# ---------------------------------------------------------------------------

def test_laterality_preserved():
    source = "Patient has pain in the left knee."
    transformed = "Patient reports left knee pain."

    findings = _findings(source, transformed)

    assert not any(
        f.drift_type == "Laterality drift"
        for f in findings
    )


def test_laterality_change_detected():
    source = "Patient has pain in the left knee."
    transformed = "Patient has pain in the right knee."

    findings = _findings(source, transformed)

    assert any(
        f.drift_type == "Laterality drift"
        for f in findings
    )


# ---------------------------------------------------------------------------
# 8. Measurement drift
# ---------------------------------------------------------------------------

def test_blood_pressure_preserved():
    source = "Blood pressure is 122/78."
    transformed = "Blood pressure is 122 / 78."

    assert _findings(source, transformed) == []


def test_blood_pressure_change_detected():
    source = "Blood pressure is 122/78."
    transformed = "Blood pressure is 180/110."

    findings = _findings(source, transformed)

    assert any(
        f.drift_type == "Measurement drift"
        and f.severity == "Critical"
        for f in findings
    )


# ---------------------------------------------------------------------------
# 9. Unsupported clinical facts
# ---------------------------------------------------------------------------

def test_new_dosage_without_source_is_flagged():
    source = "Patient reports headaches."
    transformed = "Patient reports headaches and takes 500 mg."

    findings = _findings(source, transformed)

    assert any(
        f.drift_type == "Unsupported addition"
        and f.transformed_value == "500mg"
        for f in findings
    )


def test_new_measurement_without_source_is_flagged():
    source = "Patient reports headaches."
    transformed = "Patient reports headaches. Blood pressure is 180/110."

    findings = _findings(source, transformed)

    assert any(
        f.drift_type == "Unsupported addition"
        and f.transformed_value == "180/110"
        for f in findings
    )


# ---------------------------------------------------------------------------
# 10. Complex adversarial records
# ---------------------------------------------------------------------------

def test_complex_preserved_record_reordering():
    source = (
        "Patient takes metformin 500 mg twice a day. "
        "Patient is allergic to penicillin. "
        "Blood pressure is 122/78. "
        "Symptoms have persisted for 7 days."
    )

    transformed = (
        "Blood pressure is 122/78. "
        "Symptoms have persisted for one week. "
        "Patient is allergic to penicillin. "
        "Patient takes metformin 500mg two times daily."
    )

    findings = _findings(source, transformed)

    assert findings == []


def test_complex_multi_drift_record():
    source = (
        "Patient takes metformin 500 mg twice a day. "
        "Patient is allergic to penicillin. "
        "Blood pressure is 122/78. "
        "Symptoms have persisted for 3 days."
    )

    transformed = (
        "Patient takes metformin 1000 mg once a day. "
        "Patient has no known drug allergies. "
        "Blood pressure is 180/110. "
        "Symptoms have persisted for 7 days."
    )

    findings = _findings(source, transformed)

    assert len(findings) >= 5

    types = _types(findings)

    assert "Dosage drift" in types
    assert "Frequency drift" in types
    assert "Measurement drift" in types
    assert "Duration drift" in types
    assert "Allergy contradiction" in types

    assert len(_critical(findings)) >= 3


# ---------------------------------------------------------------------------
# 11. False-positive resistance
# ---------------------------------------------------------------------------

def test_sentence_reordering_does_not_create_drift():
    source = (
        "Patient takes metformin 500 mg twice a day. "
        "Blood pressure is 122/78."
    )

    transformed = (
        "Blood pressure is 122/78. "
        "Patient takes metformin 500 mg twice a day."
    )

    assert _findings(source, transformed) == []


def test_case_changes_do_not_create_drift():
    source = "Patient takes Metformin 500 MG twice a day."
    transformed = "patient takes metformin 500 mg twice a day."

    assert _findings(source, transformed) == []


def test_punctuation_changes_do_not_create_drift():
    source = "Patient takes metformin 500 mg twice a day."
    transformed = "Patient takes metformin 500 mg twice a day!"

    assert _findings(source, transformed) == []