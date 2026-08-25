"""
ClinDrift semantic drift engine.

Compares clinical facts extracted from source and transformed text and
identifies potentially safety-relevant changes.

ClinDrift is a research prototype. Findings are indicators for human
review and are not clinical diagnoses or medical-device outputs.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from rapidfuzz.fuzz import ratio

from .extractor import ClinicalFact


# ---------------------------------------------------------------------------
# Finding model
# ---------------------------------------------------------------------------

@dataclass
class DriftFinding:
    drift_type: str
    severity: str
    source_value: str
    transformed_value: str
    source_evidence: str
    transformed_evidence: str
    rationale: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Severity model
# ---------------------------------------------------------------------------

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

DIRECT_COMPARE_CATEGORIES = {
    "dosage",
    "duration",
    "frequency",
    "laterality",
    "measurement",
}


def _severity(category: str) -> str:
    category = category.lower().strip()

    if category in CRITICAL_CATEGORIES:
        return "Critical"

    if category in HIGH_CATEGORIES:
        return "High"

    return "Medium"


# ---------------------------------------------------------------------------
# General normalisation
# ---------------------------------------------------------------------------

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
}


def _normalise_space(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def _number_value(value: str) -> Optional[float]:
    value = value.strip().lower()

    if value in NUMBER_WORDS:
        return float(NUMBER_WORDS[value])

    try:
        return float(value)
    except ValueError:
        return None


def _format_number(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))

    return str(round(value, 6)).rstrip("0").rstrip(".")


# ---------------------------------------------------------------------------
# Dosage normalisation
# ---------------------------------------------------------------------------

DOSAGE_RE = re.compile(
    r"\b(?P<number>\d+(?:\.\d+)?)\s*"
    r"(?P<unit>mcg|mg|g|ml|unit|units)\b",
    re.I,
)

DOSAGE_FACTORS_TO_MG = {
    "mcg": 0.001,
    "mg": 1.0,
    "g": 1000.0,
}


def _canonical_dosage(value: str) -> str:
    normalised = _normalise_space(value)
    match = DOSAGE_RE.search(normalised)

    if not match:
        return normalised.replace(" ", "")

    number = float(match.group("number"))
    unit = match.group("unit").lower()

    # Mass doses can safely be represented using a common comparison unit.
    if unit in DOSAGE_FACTORS_TO_MG:
        mg_value = number * DOSAGE_FACTORS_TO_MG[unit]
        return f"{_format_number(mg_value)}mg"

    if unit in {"unit", "units"}:
        return f"{_format_number(number)}units"

    if unit == "ml":
        return f"{_format_number(number)}ml"

    return normalised.replace(" ", "")


# ---------------------------------------------------------------------------
# Measurement normalisation
# ---------------------------------------------------------------------------

BP_RE = re.compile(
    r"\b(?P<systolic>\d{2,3})\s*/\s*(?P<diastolic>\d{2,3})\b"
)


def _canonical_measurement(value: str) -> str:
    normalised = _normalise_space(value)
    match = BP_RE.search(normalised)

    if match:
        return (
            f"{int(match.group('systolic'))}/"
            f"{int(match.group('diastolic'))}"
        )

    return normalised.replace(" ", "")


# ---------------------------------------------------------------------------
# Laterality normalisation
# ---------------------------------------------------------------------------

LATERALITY_MAP = {
    "left": "left",
    "right": "right",
    "bilateral": "bilateral",
    "both": "bilateral",
    "both sides": "bilateral",
}


def _canonical_laterality(value: str) -> str:
    normalised = _normalise_space(value)
    return LATERALITY_MAP.get(normalised, normalised)


# ---------------------------------------------------------------------------
# Duration normalisation
# ---------------------------------------------------------------------------

DURATION_RE = re.compile(
    r"\b(?P<number>"
    r"\d+(?:\.\d+)?|"
    r"zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve"
    r")\s+"
    r"(?P<unit>hours?|days?|weeks?|months?|years?)\b",
    re.I,
)

# Hours provide a deterministic comparison representation.
#
# Month/year conversions are intentionally approximate. ClinDrift uses these
# only for semantic-equivalence comparison in this research prototype.
DURATION_TO_HOURS = {
    "hour": 1.0,
    "hours": 1.0,
    "day": 24.0,
    "days": 24.0,
    "week": 168.0,
    "weeks": 168.0,
    "month": 730.0,
    "months": 730.0,
    "year": 8760.0,
    "years": 8760.0,
}


def _canonical_duration(value: str) -> str:
    normalised = _normalise_space(value)
    match = DURATION_RE.search(normalised)

    if not match:
        return normalised

    number = _number_value(match.group("number"))

    if number is None:
        return normalised

    unit = match.group("unit").lower()
    factor = DURATION_TO_HOURS.get(unit)

    if factor is None:
        return normalised

    hours = number * factor

    return f"{_format_number(hours)}h"


# ---------------------------------------------------------------------------
# Frequency normalisation
# ---------------------------------------------------------------------------

FREQUENCY_ALIASES = {
    # Once daily
    "once a day": "1/day",
    "once per day": "1/day",
    "once daily": "1/day",
    "one time a day": "1/day",
    "one time per day": "1/day",
    "one time daily": "1/day",
    "daily": "1/day",

    # Twice daily
    "twice a day": "2/day",
    "twice per day": "2/day",
    "twice daily": "2/day",
    "two times a day": "2/day",
    "two times per day": "2/day",
    "two times daily": "2/day",

    # Three times daily
    "three times a day": "3/day",
    "three times per day": "3/day",
    "three times daily": "3/day",

    # Four times daily
    "four times a day": "4/day",
    "four times per day": "4/day",
    "four times daily": "4/day",

    # Weekly
    "once a week": "1/week",
    "once per week": "1/week",
    "once weekly": "1/week",
    "weekly": "1/week",

    # Common day-part expressions.
    "nightly": "1/night",
    "every night": "1/night",
    "morning": "1/morning",
    "every morning": "1/morning",
    "evening": "1/evening",
    "every evening": "1/evening",
}


FREQUENCY_PATTERN = re.compile(
    r"\b(?P<count>"
    r"once|twice|"
    r"one|two|three|four|five|six|seven|eight|nine|ten|"
    r"\d+"
    r")"
    r"(?:\s+times?)?"
    r"\s+(?:a|per)?\s*"
    r"(?P<period>day|week|month)\b",
    re.I,
)


def _frequency_count(value: str) -> Optional[int]:
    value = value.lower()

    special = {
        "once": 1,
        "twice": 2,
    }

    if value in special:
        return special[value]

    number = _number_value(value)

    if number is None:
        return None

    if not float(number).is_integer():
        return None

    return int(number)


def _canonical_frequency(value: str) -> str:
    normalised = _normalise_space(value)

    # Remove punctuation that should not affect meaning.
    normalised = normalised.strip(" .,:;")

    if normalised in FREQUENCY_ALIASES:
        return FREQUENCY_ALIASES[normalised]

    # Handle expressions such as "two times daily".
    daily_match = re.fullmatch(
        r"(?P<count>"
        r"once|twice|one|two|three|four|five|six|seven|eight|nine|ten|\d+"
        r")"
        r"(?:\s+times?)?\s+daily",
        normalised,
        re.I,
    )

    if daily_match:
        count = _frequency_count(daily_match.group("count"))

        if count is not None:
            return f"{count}/day"

    weekly_match = re.fullmatch(
        r"(?P<count>"
        r"once|twice|one|two|three|four|five|six|seven|eight|nine|ten|\d+"
        r")"
        r"(?:\s+times?)?\s+weekly",
        normalised,
        re.I,
    )

    if weekly_match:
        count = _frequency_count(weekly_match.group("count"))

        if count is not None:
            return f"{count}/week"

    match = FREQUENCY_PATTERN.fullmatch(normalised)

    if match:
        count = _frequency_count(match.group("count"))

        if count is not None:
            period = match.group("period").lower()
            return f"{count}/{period}"

    return normalised


# ---------------------------------------------------------------------------
# Category-aware canonicalisation
# ---------------------------------------------------------------------------

def _canonical_value(category: str, value: str) -> str:
    category = category.lower().strip()

    if category == "dosage":
        return _canonical_dosage(value)

    if category == "measurement":
        return _canonical_measurement(value)

    if category == "duration":
        return _canonical_duration(value)

    if category == "frequency":
        return _canonical_frequency(value)

    if category == "laterality":
        return _canonical_laterality(value)

    return _normalise_space(value)


def _equivalent(category: str, first: str, second: str) -> bool:
    return _canonical_value(category, first) == _canonical_value(
        category,
        second,
    )


# ---------------------------------------------------------------------------
# Fact grouping and matching
# ---------------------------------------------------------------------------

def _group(
    facts: Sequence[ClinicalFact],
) -> Dict[str, List[ClinicalFact]]:
    grouped: Dict[str, List[ClinicalFact]] = {}

    for fact in facts:
        grouped.setdefault(fact.category, []).append(fact)

    return grouped


def _similarity(
    category: str,
    first: str,
    second: str,
) -> float:
    first_canonical = _canonical_value(category, first)
    second_canonical = _canonical_value(category, second)

    if first_canonical == second_canonical:
        return 100.0

    return float(ratio(first_canonical, second_canonical))


def _best_similarity(
    category: str,
    value: str,
    candidates: Sequence[ClinicalFact],
) -> float:
    if not candidates:
        return 0.0

    return max(
        _similarity(category, value, candidate.value)
        for candidate in candidates
    )


def _best_match(
    category: str,
    fact: ClinicalFact,
    candidates: Sequence[ClinicalFact],
) -> Tuple[Optional[ClinicalFact], float]:
    if not candidates:
        return None, 0.0

    ranked = sorted(
        candidates,
        key=lambda candidate: _similarity(
            category,
            fact.value,
            candidate.value,
        ),
        reverse=True,
    )

    best = ranked[0]

    return (
        best,
        _similarity(category, fact.value, best.value),
    )


# ---------------------------------------------------------------------------
# Finding creation
# ---------------------------------------------------------------------------

def _add(
    findings: List[DriftFinding],
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


# ---------------------------------------------------------------------------
# Allergy contradiction handling
# ---------------------------------------------------------------------------

def _is_no_known_allergy(fact: ClinicalFact) -> bool:
    value = _normalise_space(fact.value)

    return (
        "allerg" in value
        and (
            "no known" in value
            or "no drug" in value
            or "without known" in value
        )
    )


def _handle_allergy_contradictions(
    findings: List[DriftFinding],
    sgroup: Dict[str, List[ClinicalFact]],
    tgroup: Dict[str, List[ClinicalFact]],
):
    s_allergies = sgroup.get("allergy", [])
    t_allergies = tgroup.get("allergy", [])

    s_negations = sgroup.get("negation", [])
    t_negations = tgroup.get("negation", [])

    s_no_allergy = next(
        (
            fact
            for fact in s_negations
            if _is_no_known_allergy(fact)
        ),
        None,
    )

    t_no_allergy = next(
        (
            fact
            for fact in t_negations
            if _is_no_known_allergy(fact)
        ),
        None,
    )

    handled_source_allergies = set()
    handled_transformed_allergies = set()
    handled_source_negations = set()
    handled_transformed_negations = set()

    if s_allergies and t_no_allergy:
        for source_fact in s_allergies:
            _add(
                findings=findings,
                drift_type="Allergy contradiction",
                category="allergy",
                source_value=source_fact.value,
                transformed_value=t_no_allergy.value,
                source_evidence=source_fact.evidence,
                transformed_evidence=t_no_allergy.evidence,
                rationale=(
                    "A documented allergy was transformed into a "
                    "statement indicating no known allergies."
                ),
                severity="Critical",
            )

            handled_source_allergies.add(id(source_fact))

        handled_transformed_negations.add(id(t_no_allergy))

    if s_no_allergy and t_allergies:
        for transformed_fact in t_allergies:
            _add(
                findings=findings,
                drift_type="Allergy contradiction",
                category="allergy",
                source_value=s_no_allergy.value,
                transformed_value=transformed_fact.value,
                source_evidence=s_no_allergy.evidence,
                transformed_evidence=transformed_fact.evidence,
                rationale=(
                    "The source indicates no known allergies, but the "
                    "transformed text introduces an allergy."
                ),
                severity="Critical",
            )

            handled_transformed_allergies.add(id(transformed_fact))

        handled_source_negations.add(id(s_no_allergy))

    return (
        handled_source_allergies,
        handled_transformed_allergies,
        handled_source_negations,
        handled_transformed_negations,
    )


# ---------------------------------------------------------------------------
# Main comparison engine
# ---------------------------------------------------------------------------

def compare_facts(
    source: List[ClinicalFact],
    transformed: List[ClinicalFact],
) -> List[DriftFinding]:
    """
    Compare clinical facts extracted from source and transformed text.

    The comparison distinguishes between:

    * preserved facts
    * semantically equivalent representations
    * value drift
    * omissions
    * unsupported additions
    * explicit allergy contradictions

    Exact clinical correctness is not inferred. Findings indicate
    differences requiring review.
    """

    findings: List[DriftFinding] = []

    sgroup = _group(source)
    tgroup = _group(transformed)

    (
        handled_source_allergies,
        handled_transformed_allergies,
        handled_source_negations,
        handled_transformed_negations,
    ) = _handle_allergy_contradictions(
        findings,
        sgroup,
        tgroup,
    )

    categories = sorted(set(sgroup) | set(tgroup))

    for category in categories:
        sitems = list(sgroup.get(category, []))
        titems = list(tgroup.get(category, []))

        # Remove allergy/negation facts already consumed by explicit
        # contradiction handling.
        if category == "allergy":
            sitems = [
                fact
                for fact in sitems
                if id(fact) not in handled_source_allergies
            ]

            titems = [
                fact
                for fact in titems
                if id(fact) not in handled_transformed_allergies
            ]

        elif category == "negation":
            sitems = [
                fact
                for fact in sitems
                if id(fact) not in handled_source_negations
            ]

            titems = [
                fact
                for fact in titems
                if id(fact) not in handled_transformed_negations
            ]

        # ---------------------------------------------------------------
        # Direct comparison
        # ---------------------------------------------------------------
        #
        # When exactly one value exists on each side for a structured
        # category, compare canonical semantic representations first.
        #
        # Examples:
        #
        #   500 mg        == 500mg
        #   7 days        == one week
        #   twice a day   == two times daily
        #   122 / 78      == 122/78
        #
        # Genuine changes remain detectable:
        #
        #   500mg         != 1000mg
        #   twice a day   != once a day
        #   left          != right
        #
        if (
            category in DIRECT_COMPARE_CATEGORIES
            and len(sitems) == 1
            and len(titems) == 1
        ):
            source_fact = sitems[0]
            transformed_fact = titems[0]

            if not _equivalent(
                category,
                source_fact.value,
                transformed_fact.value,
            ):
                _add(
                    findings=findings,
                    drift_type=f"{category.title()} drift",
                    category=category,
                    source_value=source_fact.value,
                    transformed_value=transformed_fact.value,
                    source_evidence=source_fact.evidence,
                    transformed_evidence=transformed_fact.evidence,
                    rationale=(
                        f"The {category} value changed during "
                        "transformation."
                    ),
                )

            continue

        # ---------------------------------------------------------------
        # Source omissions
        # ---------------------------------------------------------------

        for source_fact in sitems:
            similarity = _best_similarity(
                category,
                source_fact.value,
                titems,
            )

            if not titems or similarity < 55:
                _add(
                    findings=findings,
                    drift_type="Omission",
                    category=category,
                    source_value=source_fact.value,
                    transformed_value="—",
                    source_evidence=source_fact.evidence,
                    transformed_evidence="—",
                    rationale=(
                        f"Source {category} fact is not preserved "
                        "in the transformed text."
                    ),
                )

        # ---------------------------------------------------------------
        # Unsupported additions
        # ---------------------------------------------------------------

        for transformed_fact in titems:
            similarity = _best_similarity(
                category,
                transformed_fact.value,
                sitems,
            )

            if not sitems or similarity < 55:
                _add(
                    findings=findings,
                    drift_type="Unsupported addition",
                    category=category,
                    source_value="—",
                    transformed_value=transformed_fact.value,
                    source_evidence="—",
                    transformed_evidence=transformed_fact.evidence,
                    rationale=(
                        f"Transformed text introduces a {category} "
                        "fact not found in the source."
                    ),
                )

        # ---------------------------------------------------------------
        # Material value changes
        # ---------------------------------------------------------------

        if sitems and titems:
            for source_fact in sitems:
                transformed_fact, similarity = _best_match(
                    category,
                    source_fact,
                    titems,
                )

                if transformed_fact is None:
                    continue

                if _equivalent(
                    category,
                    source_fact.value,
                    transformed_fact.value,
                ):
                    continue

                if 55 <= similarity < 100:
                    _add(
                        findings=findings,
                        drift_type=f"{category.title()} drift",
                        category=category,
                        source_value=source_fact.value,
                        transformed_value=transformed_fact.value,
                        source_evidence=source_fact.evidence,
                        transformed_evidence=transformed_fact.evidence,
                        rationale=(
                            f"The {category} value changed during "
                            "transformation."
                        ),
                    )

    # -------------------------------------------------------------------
    # Deduplicate findings
    # -------------------------------------------------------------------

    unique: List[DriftFinding] = []
    seen = set()

    for item in findings:
        key = (
            item.drift_type,
            item.severity,
            item.source_value,
            item.transformed_value,
            item.source_evidence,
            item.transformed_evidence,
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(item)

    return unique