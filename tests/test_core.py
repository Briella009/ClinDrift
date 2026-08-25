from src.extractor import extract_facts
from src.drift_engine import compare_facts


def _findings(source: str, transformed: str):
    return compare_facts(
        extract_facts(source),
        extract_facts(transformed),
    )


def test_detects_dose_drift():
    source = "Patient takes metformin 500 mg twice a day."
    transformed = "Patient takes metformin 1000 mg twice a day."

    findings = _findings(source, transformed)

    dosage_findings = [
        f for f in findings
        if f.drift_type == "Dosage drift"
    ]

    assert dosage_findings
    assert dosage_findings[0].source_value == "500mg"
    assert dosage_findings[0].transformed_value == "1000mg"
    assert dosage_findings[0].severity == "Critical"


def test_preserved_measurement_not_flagged():
    source = "Blood pressure is 122/78."
    transformed = "The patient's blood pressure is 122/78."

    findings = _findings(source, transformed)

    measurement_findings = [
        f for f in findings
        if f.drift_type == "Measurement drift"
    ]

    assert measurement_findings == []


def test_allergy_contradiction():
    source = "Patient is allergic to penicillin."
    transformed = "Patient has no known drug allergies."

    findings = _findings(source, transformed)

    allergy_findings = [
        f for f in findings
        if f.drift_type == "Allergy contradiction"
    ]

    assert allergy_findings
    assert allergy_findings[0].severity == "Critical"


def test_duration_drift():
    source = "Patient reports headaches for 3 days."
    transformed = "Patient reports headaches for 7 days."

    findings = _findings(source, transformed)

    duration_findings = [
        f for f in findings
        if f.drift_type == "Duration drift"
    ]

    assert duration_findings
    assert duration_findings[0].source_value == "3 days"
    assert duration_findings[0].transformed_value == "7 days"


def test_semantic_duration_equivalence():
    source = "Symptoms have persisted for 7 days."
    transformed = "Symptoms have persisted for one week."

    findings = _findings(source, transformed)

    duration_findings = [
        f for f in findings
        if "Duration" in f.drift_type
        or (
            f.drift_type == "Omission"
            and f.source_value in {"7 days", "one week"}
        )
        or (
            f.drift_type == "Unsupported addition"
            and f.transformed_value in {"7 days", "one week"}
        )
    ]

    assert duration_findings == []


def test_semantic_frequency_equivalence():
    source = "Patient takes metformin 500 mg twice a day."
    transformed = "Patient takes metformin 500 mg two times daily."

    findings = _findings(source, transformed)

    frequency_findings = [
        f for f in findings
        if "Frequency" in f.drift_type
        or (
            f.drift_type == "Omission"
            and f.source_value in {"twice a day", "two times daily"}
        )
        or (
            f.drift_type == "Unsupported addition"
            and f.transformed_value in {"twice a day", "two times daily"}
        )
    ]

    assert frequency_findings == []


def test_real_frequency_change_still_detected():
    source = "Patient takes metformin 500 mg twice a day."
    transformed = "Patient takes metformin 500 mg once a day."

    findings = _findings(source, transformed)

    frequency_findings = [
        f for f in findings
        if f.drift_type == "Frequency drift"
    ]

    assert frequency_findings
    assert frequency_findings[0].severity == "High"


def test_cross_unit_duration_equivalence():
    source = "Symptoms have persisted for 7 days."
    transformed = "Symptoms have persisted for one week."

    findings = _findings(source, transformed)

    duration_findings = [
        f for f in findings
        if "Duration" in f.drift_type
        or (
            f.drift_type == "Omission"
            and f.source_value in {"7 days", "one week"}
        )
        or (
            f.drift_type == "Unsupported addition"
            and f.transformed_value in {"7 days", "one week"}
        )
    ]

    assert duration_findings == []


def test_equivalent_dosage_spacing_not_flagged():
    source = "Patient takes metformin 500 mg twice a day."
    transformed = "Patient takes metformin 500mg twice a day."

    findings = _findings(source, transformed)

    dosage_findings = [
        f for f in findings
        if f.drift_type == "Dosage drift"
    ]

    assert dosage_findings == []


def test_equivalent_blood_pressure_spacing_not_flagged():
    source = "Blood pressure is 122/78."
    transformed = "Blood pressure is 122 / 78."

    findings = _findings(source, transformed)

    measurement_findings = [
        f for f in findings
        if f.drift_type == "Measurement drift"
    ]

    assert measurement_findings == []


def test_medication_omission_detected():
    source = "Patient takes metformin 500 mg twice a day."
    transformed = "Patient is clinically stable."

    findings = _findings(source, transformed)

    medication_findings = [
        f for f in findings
        if f.drift_type == "Omission"
        and f.source_value == "metformin"
    ]

    assert medication_findings
    assert medication_findings[0].severity == "High"


def test_unsupported_medication_addition_detected():
    source = "Patient reports headache for 3 days."
    transformed = "Patient reports headache for 3 days and takes warfarin."

    findings = _findings(source, transformed)

    medication_findings = [
        f for f in findings
        if f.drift_type == "Unsupported addition"
        and f.transformed_value == "warfarin"
    ]

    assert medication_findings
    assert medication_findings[0].severity == "High"


def test_laterality_change_detected():
    source = "Patient reports left knee pain."
    transformed = "Patient reports right knee pain."

    findings = _findings(source, transformed)

    laterality_findings = [
        f for f in findings
        if f.drift_type == "Laterality drift"
    ]

    assert laterality_findings
    assert laterality_findings[0].source_value == "left"
    assert laterality_findings[0].transformed_value == "right"


def test_preserved_laterality_not_flagged():
    source = "Patient reports left knee pain."
    transformed = "The patient continues to report pain in the left knee."

    findings = _findings(source, transformed)

    laterality_findings = [
        f for f in findings
        if "Laterality" in f.drift_type
    ]

    assert laterality_findings == []


def test_no_known_allergies_to_allergy_is_critical():
    source = "Patient has no known drug allergies."
    transformed = "Patient is allergic to penicillin."

    findings = _findings(source, transformed)

    allergy_findings = [
        f for f in findings
        if f.drift_type == "Allergy contradiction"
    ]

    assert allergy_findings
    assert allergy_findings[0].severity == "Critical"


def test_allergy_to_no_known_allergies_is_critical():
    source = "Patient is allergic to penicillin."
    transformed = "Patient has no known drug allergies."

    findings = _findings(source, transformed)

    allergy_findings = [
        f for f in findings
        if f.drift_type == "Allergy contradiction"
    ]

    assert allergy_findings
    assert allergy_findings[0].severity == "Critical"


def test_multiple_medications_preserved():
    source = (
        "Patient takes metformin 500 mg twice a day. "
        "Patient also takes amlodipine."
    )

    transformed = (
        "Current medicines include amlodipine and "
        "metformin 500 mg twice daily."
    )

    findings = _findings(source, transformed)

    medication_findings = [
        f for f in findings
        if f.drift_type in {"Omission", "Unsupported addition"}
        and (
            f.source_value in {"metformin", "amlodipine"}
            or f.transformed_value in {"metformin", "amlodipine"}
        )
    ]

    assert medication_findings == []


def test_measurement_change_detected():
    source = "Blood pressure is 122/78."
    transformed = "Blood pressure is 180/110."

    findings = _findings(source, transformed)

    measurement_findings = [
        f for f in findings
        if f.drift_type == "Measurement drift"
    ]

    assert measurement_findings
    assert measurement_findings[0].severity == "Critical"
    assert measurement_findings[0].source_value == "122/78"
    assert measurement_findings[0].transformed_value == "180/110"


def test_duration_paraphrase_preserved():
    source = "Patient reports headaches for 3 days."
    transformed = "The headaches have been present for three days."

    findings = _findings(source, transformed)

    duration_findings = [
        f for f in findings
        if "Duration" in f.drift_type
        or (
            f.drift_type == "Omission"
            and f.source_value in {"3 days", "three days"}
        )
        or (
            f.drift_type == "Unsupported addition"
            and f.transformed_value in {"3 days", "three days"}
        )
    ]

    assert duration_findings == []


def test_frequency_paraphrase_preserved():
    source = "Patient takes metformin 500 mg twice a day."
    transformed = "Metformin 500 mg is taken two times daily."

    findings = _findings(source, transformed)

    frequency_findings = [
        f for f in findings
        if "Frequency" in f.drift_type
        or (
            f.drift_type == "Omission"
            and f.source_value in {"twice a day", "two times daily"}
        )
        or (
            f.drift_type == "Unsupported addition"
            and f.transformed_value in {"twice a day", "two times daily"}
        )
    ]

    assert frequency_findings == []


def test_complex_multi_drift_record():
    source = (
        "Patient is allergic to penicillin. "
        "Patient takes metformin 500 mg twice a day. "
        "Blood pressure is 122/78. "
        "Patient reports left knee pain."
    )

    transformed = (
        "Patient has no known drug allergies. "
        "Patient takes metformin 1000 mg once a day. "
        "Blood pressure is 180/110. "
        "Patient reports right knee pain."
    )

    findings = _findings(source, transformed)

    drift_types = {f.drift_type for f in findings}

    assert "Allergy contradiction" in drift_types
    assert "Dosage drift" in drift_types
    assert "Frequency drift" in drift_types
    assert "Measurement drift" in drift_types
    assert "Laterality drift" in drift_types

    critical_findings = [
        f for f in findings
        if f.severity == "Critical"
    ]

    assert len(critical_findings) >= 3