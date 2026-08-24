from typing import Iterable
from .drift_engine import DriftFinding

PENALTIES = {
    "Critical": 18,
    "High": 10,
    "Medium": 6,
    "Low": 3,
}


def integrity_score(findings: Iterable[DriftFinding]) -> int:
    score = 100
    for finding in findings:
        score -= PENALTIES.get(finding.severity, 5)
    return max(0, score)


def review_status(score: int, findings: Iterable[DriftFinding]) -> str:
    findings = list(findings)
    if any(f.severity == "Critical" for f in findings):
        return "Human review required"
    if score < 80:
        return "Human review recommended"
    return "No major automated flags detected; clinical verification still required"
