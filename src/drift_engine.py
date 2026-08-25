from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from rapidfuzz.fuzz import ratio

from .extractor import ClinicalFact


# =============================================================================
# DATA MODEL
# =============================================================================


@dataclass(frozen=True)
class DriftFinding:
    """
    Represents one clinically relevant information-integrity difference between
    a source record and a transformed/AI-generated record.

    ClinDrift is an assurance prototype. A finding does not establish clinical
    correctness or incorrectness; it identifies a difference that may require
    human review.
    """

    drift_type: str
    severity: str
    source_value: str
    transformed_value: str
    source_evidence: str
    transformed_evidence: str
    rationale: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


# =============================================================================
# CONFIGURATION
# =============================================================================


CRITICAL_CATEGORIES = {
    "allergy",
    "dosage",
    "measurement",
    "negation",
}

HIGH_CATEGORIES = {
    "medication",
    "frequency",
    "laterality",
    "duration",
}

MEDIUM_CATEGORIES = {
    "condition",
    "symptom",
    "procedure",
}

DIRECT_COMPARE_CATEGORIES = {
    "dosage",
    "duration",
    "frequency",
    "laterality",
    "measurement",
}

PLACEHOLDER = "—"

FUZZY_MATCH_THRESHOLD = 70.0


# =============================================================================
# NUMBER AND UNIT NORMALISATION
# =============================================================================


NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}


DOSAGE_RE = re.compile(
    r"\b(?P<number>\d+(?:\.\d+)?)\s*"
    r"(?P<unit>mg|mcg|g|kg|ml|l|units?)\b",
    re.IGNORECASE,
)

BP_RE = re.compile(
    r"\b(?P<systolic>\d{2,3})\s*/\s*(?P<diastolic>\d{2,3})\b"
)

DURATION_RE = re.compile(
    r"\b(?P<number>\d+|[a-zA-Z]+)\s+"
    r"(?P<unit>hours?|days?|weeks?|months?|years?)\b",
    re.IGNORECASE,
)

FREQUENCY_PATTERNS: Sequence[Tuple[re.Pattern[str], str]] = (
    (re.compile(r"\bonce\s+(?:a|per)\s+day\b", re.I), "1/day"),
    (re.compile(r"\bonce\s+daily\b", re.I), "1/day"),
    (re.compile(r"\btwice\s+(?:a|per)\s+day\b", re.I), "2/day"),
    (re.compile(r"\btwice\s+daily\b", re.I), "2/day"),
    (re.compile(r"\bthree\s+times\s+(?:a|per)\s+day\b", re.I), "3/day"),
    (re.compile(r"\bthree\s+times\s+daily\b", re.I), "3/day"),
    (re.compile(r"\bfour\s+times\s+(?:a|per)\s+day\b", re.I), "4/day"),
    (re.compile(r"\bfour\s+times\s+daily\b", re.I), "4/day"),
    (re.compile(r"\bdaily\b", re.I), "1/day"),
    (re.compile(r"\bevery\s+day\b", re.I), "1/day"),
    (re.compile(r"\bnightly\b", re.I), "1/night"),
    (re.compile(r"\bweekly\b", re.I), "1/week"),
)

LATERALITY_MAP = {
    "left": "left",
    "right": "right",
    "bilateral": "bilateral",
    "both": "bilateral",
    "both sides": "bilateral",
}

UNIT_ALIASES = {
    "unit": "unit",
    "units": "unit",
    "milligram": "mg",
    "milligrams": "mg",
    "microgram": "mcg",
    "micrograms": "mcg",
    "millilitre": "ml",
    "millilitres": "ml",
    "milliliter": "ml",
    "milliliters": "ml",
}


# =============================================================================
# BASIC HELPERS
# =============================================================================


def _clean_text(value: Optional[str]) -> str:
    if value is None:
        return ""

    value = str(value).strip().lower()

    value = (
        value.replace("–", "-")
        .replace("—", "-")
        .replace("’", "'")
        .replace("“", '"')
        .replace("”", '"')
    )

    value = re.sub(r"\s+", " ", value)

    return value.strip()


def _parse_number(value: str) -> Optional[float]:
    value = _clean_text(value)

    try:
        return float(value)
    except ValueError:
        pass

    if value in NUMBER_WORDS:
        return float(NUMBER_WORDS[value])

    parts = value.replace("-", " ").split()

    if not parts:
        return None

    total = 0

    for part in parts:
        if part not in NUMBER_WORDS:
            return None
        total += NUMBER_WORDS[part]

    return float(total)


def _format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return str(round(value, 6)).rstrip("0").rstrip(".")


# =============================================================================
# CATEGORY-SPECIFIC NORMALISATION
# =============================================================================


def _normalise_dosage(value: str) -> str:
    value = _clean_text(value)

    match = DOSAGE_RE.search(value)

    if not match:
        return value.replace(" ", "")

    amount = float(match.group("number"))
    unit = _clean_text(match.group("unit"))

    unit = UNIT_ALIASES.get(unit, unit)

    # Convert common mass units to mg for stable comparison.
    if unit == "g":
        amount *= 1000.0
        unit = "mg"

    elif unit == "mcg":
        amount /= 1000.0
        unit = "mg"

    return f"{_format_number(amount)}{unit}"


def _normalise_measurement(value: str) -> str:
    value = _clean_text(value)

    match = BP_RE.search(value)

    if match:
        systolic = int(match.group("systolic"))
        diastolic = int(match.group("diastolic"))
        return f"{systolic}/{diastolic}"

    return value.replace(" ", "")


def _normalise_duration(value: str) -> str:
    """
    Convert durations to a comparable canonical representation.

    Examples:
        7 days      -> 168h
        one week    -> 168h
        3 days      -> 72h
        three days  -> 72h
        24 hours    -> 24h

    Months and years use conventional approximate values for comparison within
    this prototype and should not be interpreted as clinical interval
    arithmetic.
    """

    value = _clean_text(value)

    match = DURATION_RE.search(value)

    if not match:
        return value

    amount = _parse_number(match.group("number"))

    if amount is None:
        return value

    unit = match.group("unit").lower().rstrip("s")

    hours_per_unit = {
        "hour": 1.0,
        "day": 24.0,
        "week": 24.0 * 7.0,
        "month": 24.0 * 30.0,
        "year": 24.0 * 365.0,
    }

    multiplier = hours_per_unit.get(unit)

    if multiplier is None:
        return value

    total_hours = amount * multiplier

    return f"{_format_number(total_hours)}h"


def _normalise_frequency_from_text(text: str) -> Optional[str]:
    text = _clean_text(text)

    # More specific expressions are intentionally evaluated before "daily".
    for pattern, canonical in FREQUENCY_PATTERNS:
        if pattern.search(text):
            return canonical

    return None


def _normalise_frequency(
    value: str,
    evidence: Optional[str] = None,
) -> str:
    """
    Frequency normalisation uses both the extracted value and evidence.

    The evidence fallback matters because a simple extractor may extract
    'daily' from 'twice daily'. Examining the complete sentence prevents the
    phrase from being incorrectly reduced to once daily.
    """

    if evidence:
        evidence_result = _normalise_frequency_from_text(evidence)
        if evidence_result:
            return evidence_result

    value_result = _normalise_frequency_from_text(value)

    if value_result:
        return value_result

    return _clean_text(value)


def _normalise_laterality(value: str) -> str:
    value = _clean_text(value)
    return LATERALITY_MAP.get(value, value)


def _normalise_allergy(value: str) -> str:
    value = _clean_text(value)

    value = re.sub(r"\ballergy\b", "", value)
    value = re.sub(r"\ballergic\s+to\b", "", value)

    return value.strip(" .,:;")


def _normalise_medication(value: str) -> str:
    value = _clean_text(value)

    # Remove punctuation while preserving medication names containing hyphens.
    value = re.sub(r"[^\w\s-]", "", value)

    return value.strip()


def _normalise_negation(value: str) -> str:
    value = _clean_text(value)

    if re.search(r"\bno known (?:drug )?allerg(?:y|ies)\b", value):
        return "no-known-allergies"

    return value


def _normalise_fact_value(fact: ClinicalFact) -> str:
    category = _clean_text(fact.category)
    value = fact.value

    if category == "dosage":
        return _normalise_dosage(value)

    if category == "measurement":
        return _normalise_measurement(value)

    if category == "duration":
        return _normalise_duration(value)

    if category == "frequency":
        return _normalise_frequency(value, fact.evidence)

    if category == "laterality":
        return _normalise_laterality(value)

    if category == "allergy":
        return _normalise_allergy(value)

    if category == "medication":
        return _normalise_medication(value)

    if category == "negation":
        return _normalise_negation(value)

    return _clean_text(value)


# =============================================================================
# SEVERITY
# =============================================================================


def _severity(category: str) -> str:
    category = _clean_text(category)

    if category in CRITICAL_CATEGORIES:
        return "Critical"

    if category in HIGH_CATEGORIES:
        return "High"

    if category in MEDIUM_CATEGORIES:
        return "Medium"

    return "Medium"


# =============================================================================
# FACT COLLECTION HELPERS
# =============================================================================


def _group(
    facts: Iterable[ClinicalFact],
) -> Dict[str, List[ClinicalFact]]:
    grouped: Dict[str, List[ClinicalFact]] = {}

    for fact in facts:
        category = _clean_text(fact.category)
        grouped.setdefault(category, []).append(fact)

    return grouped


def _fact_similarity(
    source_fact: ClinicalFact,
    transformed_fact: ClinicalFact,
) -> float:
    """
    Compare facts after category-aware normalisation.
    """

    if _clean_text(source_fact.category) != _clean_text(transformed_fact.category):
        return 0.0

    source_normalised = _normalise_fact_value(source_fact)
    transformed_normalised = _normalise_fact_value(transformed_fact)

    if source_normalised == transformed_normalised:
        return 100.0

    return float(
        ratio(
            source_normalised,
            transformed_normalised,
        )
    )


def _best_match(
    fact: ClinicalFact,
    candidates: Sequence[ClinicalFact],
) -> Tuple[Optional[ClinicalFact], float]:
    if not candidates:
        return None, 0.0

    ranked = [
        (candidate, _fact_similarity(fact, candidate))
        for candidate in candidates
    ]

    ranked.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    return ranked[0]


def _equivalent(
    source_fact: ClinicalFact,
    transformed_fact: ClinicalFact,
) -> bool:
    return (
        _normalise_fact_value(source_fact)
        == _normalise_fact_value(transformed_fact)
    )


# =============================================================================
# FINDING HELPERS
# =============================================================================


def _add_finding(
    findings: List[DriftFinding],
    *,
    drift_type: str,
    category: str,
    source_value: str,
    transformed_value: str,
    source_evidence: str,
    transformed_evidence: str,
    rationale: str,
    severity: Optional[str] = None,
) -> None:
    findings.append(
        DriftFinding(
            drift_type=drift_type,
            severity=severity or _severity(category),
            source_value=source_value,
            transformed_value=transformed_value,
            source_evidence=source_evidence,
            transformed_evidence=transformed_evidence,
            rationale=rationale,
        )
    )


def _finding_key(
    finding: DriftFinding,
) -> Tuple[str, str, str, str, str]:
    return (
        _clean_text(finding.drift_type),
        _clean_text(finding.source_value),
        _clean_text(finding.transformed_value),
        _clean_text(finding.source_evidence),
        _clean_text(finding.transformed_evidence),
    )


def _deduplicate_findings(
    findings: Iterable[DriftFinding],
) -> List[DriftFinding]:
    seen = set()
    unique: List[DriftFinding] = []

    for finding in findings:
        key = _finding_key(finding)

        if key in seen:
            continue

        seen.add(key)
        unique.append(finding)

    return unique


# =============================================================================
# ALLERGY CONTRADICTION
# =============================================================================


def _is_no_known_allergies(fact: ClinicalFact) -> bool:
    if _clean_text(fact.category) != "negation":
        return False

    combined = f"{fact.value} {fact.evidence}".lower()

    return bool(
        re.search(
            r"\bno known (?:drug )?allerg(?:y|ies)\b",
            combined,
            re.IGNORECASE,
        )
    )


def _detect_allergy_contradictions(
    source_group: Dict[str, List[ClinicalFact]],
    transformed_group: Dict[str, List[ClinicalFact]],
    findings: List[DriftFinding],
) -> Tuple[set[int], set[int], set[int], set[int]]:
    source_allergies = source_group.get("allergy", [])
    transformed_allergies = transformed_group.get("allergy", [])

    source_negations = source_group.get("negation", [])
    transformed_negations = transformed_group.get("negation", [])

    handled_source_allergies: set[int] = set()
    handled_transformed_allergies: set[int] = set()
    handled_source_negations: set[int] = set()
    handled_transformed_negations: set[int] = set()

    transformed_no_allergy = next(
        (
            fact
            for fact in transformed_negations
            if _is_no_known_allergies(fact)
        ),
        None,
    )

    source_no_allergy = next(
        (
            fact
            for fact in source_negations
            if _is_no_known_allergies(fact)
        ),
        None,
    )

    # Source states an allergy, transformed text says there are none.
    if source_allergies and transformed_no_allergy:
        for source_fact in source_allergies:
            _add_finding(
                findings,
                drift_type="Allergy contradiction",
                category="allergy",
                source_value=source_fact.value,
                transformed_value=transformed_no_allergy.value,
                source_evidence=source_fact.evidence,
                transformed_evidence=transformed_no_allergy.evidence,
                rationale=(
                    "A documented allergy was transformed into a statement "
                    "indicating no known allergies."
                ),
                severity="Critical",
            )

            handled_source_allergies.add(id(source_fact))

        handled_transformed_negations.add(id(transformed_no_allergy))

    # Source says no known allergies, transformed text introduces one.
    if source_no_allergy and transformed_allergies:
        for transformed_fact in transformed_allergies:
            _add_finding(
                findings,
                drift_type="Allergy contradiction",
                category="allergy",
                source_value=source_no_allergy.value,
                transformed_value=transformed_fact.value,
                source_evidence=source_no_allergy.evidence,
                transformed_evidence=transformed_fact.evidence,
                rationale=(
                    "The source states that there are no known allergies, "
                    "but the transformed record introduces an allergy."
                ),
                severity="Critical",
            )

            handled_transformed_allergies.add(id(transformed_fact))

        handled_source_negations.add(id(source_no_allergy))

    return (
        handled_source_allergies,
        handled_transformed_allergies,
        handled_source_negations,
        handled_transformed_negations,
    )


# =============================================================================
# DIRECT FIELD COMPARISON
# =============================================================================


def _compare_direct_category(
    category: str,
    source_items: Sequence[ClinicalFact],
    transformed_items: Sequence[ClinicalFact],
    findings: List[DriftFinding],
) -> bool:
    """
    Compare categories such as dosage, duration, frequency, laterality and
    measurement.

    Returns True when the category has been completely handled here.
    """

    if category not in DIRECT_COMPARE_CATEGORIES:
        return False

    if len(source_items) != 1 or len(transformed_items) != 1:
        return False

    source_fact = source_items[0]
    transformed_fact = transformed_items[0]

    if _equivalent(source_fact, transformed_fact):
        return True

    label_map = {
        "dosage": "Dosage drift",
        "duration": "Duration drift",
        "frequency": "Frequency drift",
        "laterality": "Laterality drift",
        "measurement": "Measurement drift",
    }

    _add_finding(
        findings,
        drift_type=label_map.get(
            category,
            f"{category.title()} drift",
        ),
        category=category,
        source_value=source_fact.value,
        transformed_value=transformed_fact.value,
        source_evidence=source_fact.evidence,
        transformed_evidence=transformed_fact.evidence,
        rationale=(
            f"The {category} value changed during transformation."
        ),
    )

    return True


# =============================================================================
# GENERAL CATEGORY COMPARISON
# =============================================================================


def _compare_general_category(
    category: str,
    source_items: Sequence[ClinicalFact],
    transformed_items: Sequence[ClinicalFact],
    findings: List[DriftFinding],
) -> None:
    """
    Match source and transformed facts using normalised semantic values.

    Unmatched source facts become omission candidates.
    Unmatched transformed facts become unsupported-addition candidates.
    Materially changed matched values become drift candidates.
    """

    unmatched_transformed = list(transformed_items)

    for source_fact in source_items:
        best_fact, similarity = _best_match(
            source_fact,
            unmatched_transformed,
        )

        if best_fact is None:
            _add_finding(
                findings,
                drift_type="Omission",
                category=category,
                source_value=source_fact.value,
                transformed_value=PLACEHOLDER,
                source_evidence=source_fact.evidence,
                transformed_evidence=PLACEHOLDER,
                rationale=(
                    f"Source {category} fact is not preserved "
                    f"in the transformed text."
                ),
            )
            continue

        # Exact canonical equivalence.
        if _equivalent(source_fact, best_fact):
            unmatched_transformed.remove(best_fact)
            continue

        # Materially similar facts in the same category are treated as a
        # changed value rather than as separate omission/addition findings.
        if similarity >= FUZZY_MATCH_THRESHOLD:
            _add_finding(
                findings,
                drift_type=f"{category.title()} drift",
                category=category,
                source_value=source_fact.value,
                transformed_value=best_fact.value,
                source_evidence=source_fact.evidence,
                transformed_evidence=best_fact.evidence,
                rationale=(
                    f"The {category} value changed during transformation."
                ),
            )

            unmatched_transformed.remove(best_fact)
            continue

        # Poor match: the source fact appears to be missing.
        _add_finding(
            findings,
            drift_type="Omission",
            category=category,
            source_value=source_fact.value,
            transformed_value=PLACEHOLDER,
            source_evidence=source_fact.evidence,
            transformed_evidence=PLACEHOLDER,
            rationale=(
                f"Source {category} fact is not preserved "
                f"in the transformed text."
            ),
        )

    # Anything left on the transformed side was not supported by source facts.
    for transformed_fact in unmatched_transformed:
        _add_finding(
            findings,
            drift_type="Unsupported addition",
            category=category,
            source_value=PLACEHOLDER,
            transformed_value=transformed_fact.value,
            source_evidence=PLACEHOLDER,
            transformed_evidence=transformed_fact.evidence,
            rationale=(
                f"The transformed text introduces a {category} fact "
                f"that was not identified in the source record."
            ),
        )


# =============================================================================
# PUBLIC COMPARISON FUNCTION
# =============================================================================


def compare_facts(
    source: List[ClinicalFact],
    transformed: List[ClinicalFact],
) -> List[DriftFinding]:
    """
    Compare extracted clinical facts from a source record and a transformed
    record.

    The comparison is intentionally conservative and evidence-oriented.

    It supports:

    - allergy contradictions
    - dosage drift
    - duration drift
    - semantic duration equivalence
    - frequency drift
    - semantic frequency equivalence
    - measurement drift
    - laterality drift
    - omissions
    - unsupported additions
    - medication drift
    - negation-related differences
    - claim-level evidence traceability

    Important:
        A zero-finding result means only that the implemented rules did not
        identify a supported difference. It is not evidence of clinical
        correctness or safety.
    """

    findings: List[DriftFinding] = []

    source_group = _group(source)
    transformed_group = _group(transformed)

    (
        handled_source_allergies,
        handled_transformed_allergies,
        handled_source_negations,
        handled_transformed_negations,
    ) = _detect_allergy_contradictions(
        source_group,
        transformed_group,
        findings,
    )

    categories = sorted(
        set(source_group.keys())
        | set(transformed_group.keys())
    )

    for category in categories:
        source_items = list(
            source_group.get(category, [])
        )

        transformed_items = list(
            transformed_group.get(category, [])
        )

        # Prevent allergy contradictions from also appearing as generic
        # omissions/additions.
        if category == "allergy":
            source_items = [
                item
                for item in source_items
                if id(item) not in handled_source_allergies
            ]

            transformed_items = [
                item
                for item in transformed_items
                if id(item) not in handled_transformed_allergies
            ]

        if category == "negation":
            source_items = [
                item
                for item in source_items
                if id(item) not in handled_source_negations
            ]

            transformed_items = [
                item
                for item in transformed_items
                if id(item) not in handled_transformed_negations
            ]

        # Nothing remains to compare.
        if not source_items and not transformed_items:
            continue

        # Handle simple one-to-one structured clinical fields first.
        handled = _compare_direct_category(
            category,
            source_items,
            transformed_items,
            findings,
        )

        if handled:
            continue

        # General fact matching handles omissions, additions and changes.
        _compare_general_category(
            category,
            source_items,
            transformed_items,
            findings,
        )

    return _deduplicate_findings(findings)