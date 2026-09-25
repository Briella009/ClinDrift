"""Safety-oriented evaluation metrics for ClinDrift experiments.

These functions complement aggregate accuracy metrics with critical-error recall,
review burden and repeated-run stability. They do not establish clinical safety.
"""

from __future__ import annotations

from itertools import combinations
from typing import Any, Iterable, Mapping, Sequence


def critical_error_recall(rows: Iterable[Mapping[str, Any]]) -> float:
    """Return recall among cases whose reference severity is Critical.

    Each row must contain ``severity`` and boolean ``flagged`` fields.
    """

    critical = [row for row in rows if row.get("severity") == "Critical"]
    if not critical:
        raise ValueError("At least one Critical reference case is required")
    return sum(bool(row.get("flagged")) for row in critical) / len(critical)


def catastrophic_miss_rate(rows: Iterable[Mapping[str, Any]]) -> float:
    """Return the proportion of Critical reference cases not flagged."""

    return 1.0 - critical_error_recall(rows)


def review_burden(rows: Iterable[Mapping[str, Any]]) -> float:
    """Return the proportion of all cases sent to review."""

    materialized = list(rows)
    if not materialized:
        raise ValueError("At least one case is required")
    return sum(bool(row.get("requires_review")) for row in materialized) / len(materialized)


def _signature(item: Any) -> tuple[str, str, str, str]:
    if isinstance(item, Mapping):
        get = item.get
    else:
        get = lambda key, default="": getattr(item, key, default)
    return (
        str(get("drift_type", "")),
        str(get("category", "")),
        str(get("source_value", "")),
        str(get("transformed_value", "")),
    )


def repeated_run_stability(runs: Sequence[Iterable[Any]]) -> float:
    """Mean pairwise Jaccard agreement across repeated finding sets.

    A score of 1 means every run produced the same set of finding signatures.
    Two or more runs are required. Two empty runs count as agreement.
    """

    if len(runs) < 2:
        raise ValueError("At least two runs are required")
    sets = [{_signature(item) for item in run} for run in runs]
    agreements = []
    for left, right in combinations(sets, 2):
        union = left | right
        agreements.append(1.0 if not union else len(left & right) / len(union))
    return sum(agreements) / len(agreements)
