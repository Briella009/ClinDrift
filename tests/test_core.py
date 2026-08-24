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
