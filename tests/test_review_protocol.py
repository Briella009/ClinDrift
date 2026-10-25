import pytest

from src.drift_engine import compare_facts
from src.extractor import extract_facts
from src.review_protocol import build_review_tasks, validate_disposition


def test_allergy_finding_creates_blocking_review_task():
    findings = compare_facts(
        extract_facts("Patient is allergic to penicillin."),
        extract_facts("No known drug allergies."),
    )
    task = build_review_tasks(findings)[0]

    assert task.category == "allergy"
    assert task.severity == "Critical"
    assert "allergy" in task.verification_question.lower()
    assert "Block automatic acceptance" in task.escalation_rule
    assert task.review_id.startswith("review-")


def test_review_ids_are_stable_for_same_finding():
    findings = compare_facts(
        extract_facts("Headache for 3 days."),
        extract_facts("Headache for 3 weeks."),
    )
    first = build_review_tasks(findings)[0]
    second = build_review_tasks(findings)[0]
    assert first.review_id == second.review_id


def test_invalid_disposition_is_rejected():
    with pytest.raises(ValueError):
        validate_disposition("Approved")
