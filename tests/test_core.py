from src.extractor import extract_facts
from src.drift_engine import compare_facts
from src.scoring import integrity_score


def test_detects_dose_drift():
    source = extract_facts("Patient takes metformin 500 mg twice a day.")
    transformed = extract_facts("Patient takes metformin 1000 mg twice a day.")
    findings = compare_facts(source, transformed)
    assert any(f.drift_type == "Dosage drift" for f in findings)
    assert integrity_score(findings) < 100


def test_preserved_measurement_not_flagged():
    source = extract_facts("Blood pressure is 122/78.")
    transformed = extract_facts("Blood pressure is 122/78.")
    findings = compare_facts(source, transformed)
    assert not findings


def test_allergy_contradiction():
    source = extract_facts("Patient is allergic to penicillin.")
    transformed = extract_facts("No known drug allergies.")
    findings = compare_facts(source, transformed)
    assert any(f.drift_type == "Allergy contradiction" and f.severity == "Critical" for f in findings)


def test_duration_drift():
    source = extract_facts("Headache for 3 days.")
    transformed = extract_facts("Headache for 3 weeks.")
    findings = compare_facts(source, transformed)
    assert any(f.drift_type == "Duration drift" for f in findings)
def test_semantic_duration_equivalence():
    from src.extractor import extract_facts
    from src.drift_engine import compare_facts

    source = extract_facts(
        "Patient reports headaches for 3 days."
    )

    transformed = extract_facts(
        "Patient reports headaches for three days."
    )

    findings = compare_facts(source, transformed)

    duration_findings = [
        finding
        for finding in findings
        if finding.drift_type == "Duration drift"
        or (
            finding.drift_type == "Omission"
            and finding.source_value in {"3 days", "three days"}
        )
    ]

    assert duration_findings == []


def test_semantic_frequency_equivalence():
    from src.extractor import extract_facts
    from src.drift_engine import compare_facts

    source = extract_facts(
        "Patient takes metformin 500 mg twice a day."
    )

    transformed = extract_facts(
        "Patient takes metformin 500 mg twice daily."
    )

    findings = compare_facts(source, transformed)

    frequency_findings = [
        finding
        for finding in findings
        if finding.drift_type == "Frequency drift"
        or (
            finding.drift_type == "Omission"
            and finding.source_value in {
                "twice a day",
                "twice daily",
            }
        )
    ]

    assert frequency_findings == []


def test_real_frequency_change_still_detected():
    from src.extractor import extract_facts
    from src.drift_engine import compare_facts

    source = extract_facts(
        "Patient takes metformin 500 mg twice a day."
    )

    transformed = extract_facts(
        "Patient takes metformin 500 mg once a day."
    )

    findings = compare_facts(source, transformed)

    frequency_findings = [
        finding
        for finding in findings
        if finding.drift_type == "Frequency drift"
    ]

    assert len(frequency_findings) == 1

    finding = frequency_findings[0]

    assert finding.source_value == "twice a day"
    assert finding.transformed_value == "once a day"
    assert finding.severity == "High"


def test_cross_unit_duration_equivalence():
    from src.extractor import extract_facts
    from src.drift_engine import compare_facts

    source = extract_facts(
        "Symptoms have persisted for 7 days."
    )

    transformed = extract_facts(
        "Symptoms have persisted for one week."
    )

    findings = compare_facts(source, transformed)

    duration_findings = [
        finding
        for finding in findings
        if finding.drift_type == "Duration drift"
        or (
            finding.drift_type == "Omission"
            and finding.source_value in {
                "7 days",
                "one week",
            }
        )
    ]

    assert duration_findings == []