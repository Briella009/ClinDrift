"""Structured human-review prompts for ClinDrift findings.

The protocol makes an escalation instruction explicit; it does not establish that
human review is effective. That claim requires a prospective user study.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Iterable

from .drift_engine import DriftFinding


PROTOCOL_VERSION = "2026-09-structured-review-v1"
ALLOWED_DISPOSITIONS = (
    "Unreviewed",
    "Confirmed integrity error",
    "Not an integrity error",
    "Insufficient evidence",
    "Escalated",
)


@dataclass(frozen=True)
class ReviewTask:
    review_id: str
    protocol_version: str
    severity: str
    category: str
    drift_type: str
    verification_question: str
    required_action: str
    escalation_rule: str
    source_evidence: str
    transformed_evidence: str
    mechanism: str = "deterministic"

    def to_dict(self) -> dict:
        return asdict(self)


CATEGORY_GUIDANCE = {
    "allergy": (
        "Does the transformed allergy statement agree with the source allergy record?",
        "Reconcile the source statement with the current allergy list before the text is used.",
    ),
    "dosage": (
        "Are medication name, dose value and unit preserved exactly?",
        "Verify against the originating prescription or medication administration record.",
    ),
    "frequency": (
        "Is the medication frequency clinically equivalent to the source instruction?",
        "Verify the schedule against the originating prescription.",
    ),
    "medication": (
        "Is every medication assertion supported by the source record?",
        "Reconcile the statement with the current medication list and orders.",
    ),
    "measurement": (
        "Is the value, unit and measurement context preserved?",
        "Compare with the originating observation, result or vital-sign record.",
    ),
    "negation": (
        "Did the transformation add, remove or change a clinical negation?",
        "Read the complete source and transformed sentences and verify the intended assertion.",
    ),
    "laterality": (
        "Is the anatomical side preserved?",
        "Verify laterality against the source note and relevant clinical record.",
    ),
    "duration": (
        "Is symptom or treatment duration preserved?",
        "Verify the chronology and unit against the source history.",
    ),
}


def _review_id(finding: DriftFinding) -> str:
    payload = "|".join(
        (
            finding.drift_type,
            finding.category,
            finding.source_value,
            finding.transformed_value,
            finding.source_evidence,
            finding.transformed_evidence,
        )
    )
    return f"review-{sha256(payload.encode('utf-8')).hexdigest()[:12]}"


def _escalation_rule(severity: str) -> str:
    if severity == "Critical":
        return "Block automatic acceptance and obtain qualified clinical review."
    if severity == "High":
        return "Require explicit reviewer resolution before downstream use."
    return "Resolve the finding or document the rationale before downstream use."


def _guidance(finding: DriftFinding) -> tuple[str, str]:
    question, action = CATEGORY_GUIDANCE.get(
        finding.category,
        (
            "Is the transformed assertion supported by the cited source evidence?",
            "Compare both evidence excerpts and consult the originating record if needed.",
        ),
    )
    if finding.drift_type == "Omission":
        question = "Is the omitted source fact clinically relevant and required in the transformed text?"
        action = "Locate the source fact, confirm its relevance, then restore it or document why omission is acceptable."
    elif finding.drift_type == "Unsupported addition":
        question = "Is there source evidence for the added assertion?"
        action = "Locate supporting evidence; otherwise remove or correct the unsupported assertion."
    return question, action


def build_review_tasks(findings: Iterable[DriftFinding]) -> list[ReviewTask]:
    tasks = []
    for finding in findings:
        question, action = _guidance(finding)
        tasks.append(
            ReviewTask(
                review_id=_review_id(finding),
                protocol_version=PROTOCOL_VERSION,
                severity=finding.severity,
                category=finding.category,
                drift_type=finding.drift_type,
                verification_question=question,
                required_action=action,
                escalation_rule=_escalation_rule(finding.severity),
                source_evidence=finding.source_evidence,
                transformed_evidence=finding.transformed_evidence,
            )
        )
    return tasks


def validate_disposition(disposition: str) -> str:
    if disposition not in ALLOWED_DISPOSITIONS:
        raise ValueError(f"Unsupported reviewer disposition: {disposition}")
    return disposition
