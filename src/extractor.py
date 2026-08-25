"""
ClinDrift clinical fact extractor.

Extracts structured, comparison-oriented facts from clinical text for use
by the ClinDrift information-integrity engine.

This module intentionally uses deterministic extraction rather than
diagnostic or generative reasoning. It is designed for research,
evaluation, reproducibility, and evidence traceability.

ClinDrift is a research prototype and is not a medical device.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Dict, List, Sequence, Tuple


# ---------------------------------------------------------------------------
# Clinical fact model
# ---------------------------------------------------------------------------

@dataclass
class ClinicalFact:
    category: str
    value: str
    evidence: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Number vocabulary
# ---------------------------------------------------------------------------

NUMBER_WORDS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
}


NUMBER_TOKEN = (
    r"(?:"
    r"\d+(?:\.\d+)?|"
    r"zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve"
    r")"
)


# ---------------------------------------------------------------------------
# Dosage extraction
# ---------------------------------------------------------------------------

DOSAGE_RE = re.compile(
    rf"\b{NUMBER_TOKEN}\s*"
    r"(?:mcg|mg|g|ml|units?)\b",
    re.I,
)


# ---------------------------------------------------------------------------
# Blood pressure / measurement extraction
# ---------------------------------------------------------------------------

BP_RE = re.compile(
    r"\b"
    r"(?:[89]\d|1\d\d|2[0-4]\d)"
    r"\s*/\s*"
    r"(?:[4-9]\d|1\d\d)"
    r"\b"
)


# ---------------------------------------------------------------------------
# Duration extraction
# ---------------------------------------------------------------------------

DURATION_RE = re.compile(
    rf"\b{NUMBER_TOKEN}\s+"
    r"(?:hours?|days?|weeks?|months?|years?)\b",
    re.I,
)


# ---------------------------------------------------------------------------
# Frequency extraction
# ---------------------------------------------------------------------------
#
# IMPORTANT:
#
# Longer semantic phrases are intentionally placed BEFORE short aliases
# such as "daily".
#
# Otherwise:
#
#     "two times daily"
#
# can be extracted merely as:
#
#     "daily"
#
# which creates a false Frequency drift when compared with:
#
#     "twice a day"
#
# Both complete phrases must reach drift_engine.py so that the semantic
# canonicalisation layer can compare them correctly.
# ---------------------------------------------------------------------------

FREQUENCY_RE = re.compile(
    r"\b(?:"
    # once / twice
    r"(?:once|twice)\s+(?:a|per)\s+(?:day|week|month)"
    r"|"
    r"(?:once|twice)\s+(?:daily|weekly|monthly)"
    r"|"

    # word-number "times" expressions
    r"(?:one|two|three|four|five|six|seven|eight|nine|ten)"
    r"\s+times?\s+(?:a|per)\s+(?:day|week|month)"
    r"|"
    r"(?:one|two|three|four|five|six|seven|eight|nine|ten)"
    r"\s+times?\s+(?:daily|weekly|monthly)"
    r"|"

    # numeric "times" expressions
    r"\d+\s+times?\s+(?:a|per)\s+(?:day|week|month)"
    r"|"
    r"\d+\s+times?\s+(?:daily|weekly|monthly)"
    r"|"

    # standalone conventional frequency terms
    r"daily"
    r"|weekly"
    r"|monthly"
    r"|nightly"
    r"|every\s+night"
    r"|every\s+morning"
    r"|every\s+evening"
    r"|morning"
    r"|evening"
    r")\b",
    re.I,
)


# ---------------------------------------------------------------------------
# Laterality extraction
# ---------------------------------------------------------------------------

LATERALITY_RE = re.compile(
    r"\b(?:left|right|bilateral)\b",
    re.I,
)


# ---------------------------------------------------------------------------
# Medication vocabulary
# ---------------------------------------------------------------------------
#
# v0.2 uses a deliberately bounded medication vocabulary.
#
# This keeps extraction deterministic and auditable. Expansion should be
# evaluated rather than silently treating arbitrary words as medications.
# ---------------------------------------------------------------------------

MEDICATION_HINTS = {
    "acetaminophen",
    "amlodipine",
    "amoxicillin",
    "aspirin",
    "atorvastatin",
    "ibuprofen",
    "insulin",
    "lisinopril",
    "metformin",
    "omeprazole",
    "paracetamol",
    "penicillin",
    "warfarin",
}


# ---------------------------------------------------------------------------
# Allergy patterns
# ---------------------------------------------------------------------------

ALLERGY_PATTERNS: Sequence[re.Pattern[str]] = (
    # Patient is allergic to penicillin.
    re.compile(
        r"\ballergic\s+to\s+"
        r"([a-zA-Z][a-zA-Z0-9\-]*)",
        re.I,
    ),

    # Penicillin allergy.
    re.compile(
        r"\b([a-zA-Z][a-zA-Z0-9\-]*)\s+allerg(?:y|ies)\b",
        re.I,
    ),

    # Allergy to penicillin.
    re.compile(
        r"\ballerg(?:y|ies)\s+to\s+"
        r"([a-zA-Z][a-zA-Z0-9\-]*)",
        re.I,
    ),
)


# ---------------------------------------------------------------------------
# Negation patterns
# ---------------------------------------------------------------------------

NEGATION_PATTERNS: Sequence[re.Pattern[str]] = (
    re.compile(
        r"\bno\s+known\s+(?:drug\s+)?allerg(?:y|ies)\b",
        re.I,
    ),

    re.compile(
        r"\bdenies\s+([^.,;]+)",
        re.I,
    ),

    re.compile(
        r"\bno\s+history\s+of\s+([^.,;]+)",
        re.I,
    ),

    re.compile(
        r"\bnot\s+taking\s+([^.,;]+)",
        re.I,
    ),
)


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def _normalise_space(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def _clean_capture(value: str) -> str:
    value = _normalise_space(value)
    return value.strip(" .,:;").lower()


def _sentences(text: str) -> List[str]:
    """
    Split text into lightweight evidence spans.

    Evidence is deliberately retained at sentence level so every extracted
    fact can later be traced back to the text that produced it.
    """

    if not text:
        return []

    chunks = re.split(
        r"(?<=[.!?])\s+|\n+",
        text.strip(),
    )

    return [
        chunk.strip()
        for chunk in chunks
        if chunk.strip()
    ]


def _normalise_dosage(value: str) -> str:
    """
    Normalise spacing only.

    500 mg -> 500mg
    500mg  -> 500mg

    Unit conversion itself belongs to drift_engine.py.
    """

    value = _clean_capture(value)

    return re.sub(
        r"\s+",
        "",
        value,
    )


def _normalise_measurement(value: str) -> str:
    """
    Normalise spacing around blood-pressure separators.

    122 / 78 -> 122/78
    """

    return re.sub(
        r"\s+",
        "",
        _clean_capture(value),
    )


def _normalise_duration(value: str) -> str:
    """
    Preserve meaningful duration wording.

    Examples:

        7 days
        one week
        three days

    Cross-unit semantic conversion occurs in drift_engine.py.
    """

    return _clean_capture(value)


def _normalise_frequency(value: str) -> str:
    """
    Preserve the complete frequency phrase.

    This is important because drift_engine.py is responsible for semantic
    canonicalisation.

    Examples preserved here:

        twice a day
        two times daily
        once a day
        three times daily
    """

    return _clean_capture(value)


def _normalise_laterality(value: str) -> str:
    return _clean_capture(value)


# ---------------------------------------------------------------------------
# Allergy span handling
# ---------------------------------------------------------------------------

def _extract_allergies(
    sentence: str,
) -> Tuple[List[ClinicalFact], List[Tuple[int, int]]]:
    """
    Extract allergies and return both facts and matched spans.

    The spans are used to prevent a drug appearing only as an allergen from
    also being incorrectly classified as an active medication.

    Example:

        Patient is allergic to penicillin.

    should produce:

        allergy -> penicillin

    but should NOT also produce:

        medication -> penicillin
    """

    facts: List[ClinicalFact] = []
    spans: List[Tuple[int, int]] = []

    for pattern in ALLERGY_PATTERNS:
        for match in pattern.finditer(sentence):
            value = _clean_capture(match.group(1))

            if not value:
                continue

            facts.append(
                ClinicalFact(
                    category="allergy",
                    value=value,
                    evidence=sentence,
                )
            )

            spans.append(match.span())

    return facts, spans


def _inside_any_span(
    start: int,
    end: int,
    spans: Sequence[Tuple[int, int]],
) -> bool:
    for span_start, span_end in spans:
        if start >= span_start and end <= span_end:
            return True

    return False


# ---------------------------------------------------------------------------
# Main extractor
# ---------------------------------------------------------------------------

def extract_facts(text: str) -> List[ClinicalFact]:
    """
    Extract comparison-oriented clinical facts from text.

    Current v0.2 categories:

        allergy
        negation
        medication
        dosage
        measurement
        duration
        frequency
        laterality

    Each fact retains its source evidence span.
    """

    facts: List[ClinicalFact] = []

    for sentence in _sentences(text):
        lower = sentence.lower()

        # -----------------------------------------------------------------
        # Allergies first
        # -----------------------------------------------------------------

        allergy_facts, allergy_spans = _extract_allergies(sentence)

        facts.extend(allergy_facts)

        # -----------------------------------------------------------------
        # Negation
        # -----------------------------------------------------------------

        for pattern in NEGATION_PATTERNS:
            for match in pattern.finditer(sentence):
                value = _clean_capture(match.group(0))

                if value:
                    facts.append(
                        ClinicalFact(
                            category="negation",
                            value=value,
                            evidence=sentence,
                        )
                    )

        # -----------------------------------------------------------------
        # Medication
        # -----------------------------------------------------------------

        for medication in sorted(MEDICATION_HINTS):
            medication_re = re.compile(
                rf"\b{re.escape(medication)}\b",
                re.I,
            )

            for match in medication_re.finditer(sentence):
                # A drug mentioned solely inside an allergy statement is not
                # automatically an active medication.
                if _inside_any_span(
                    match.start(),
                    match.end(),
                    allergy_spans,
                ):
                    continue

                facts.append(
                    ClinicalFact(
                        category="medication",
                        value=medication.lower(),
                        evidence=sentence,
                    )
                )

        # -----------------------------------------------------------------
        # Dosage
        # -----------------------------------------------------------------

        for match in DOSAGE_RE.finditer(sentence):
            facts.append(
                ClinicalFact(
                    category="dosage",
                    value=_normalise_dosage(match.group(0)),
                    evidence=sentence,
                )
            )

        # -----------------------------------------------------------------
        # Measurement
        # -----------------------------------------------------------------

        for match in BP_RE.finditer(sentence):
            facts.append(
                ClinicalFact(
                    category="measurement",
                    value=_normalise_measurement(match.group(0)),
                    evidence=sentence,
                )
            )

        # -----------------------------------------------------------------
        # Duration
        # -----------------------------------------------------------------

        for match in DURATION_RE.finditer(sentence):
            facts.append(
                ClinicalFact(
                    category="duration",
                    value=_normalise_duration(match.group(0)),
                    evidence=sentence,
                )
            )

        # -----------------------------------------------------------------
        # Frequency
        # -----------------------------------------------------------------
        #
        # finditer() returns the complete longest applicable expression
        # because the compound alternatives precede standalone "daily".
        #
        # Thus:
        #
        #     two times daily
        #
        # becomes:
        #
        #     frequency = "two times daily"
        #
        # rather than merely:
        #
        #     frequency = "daily"
        #
        # -----------------------------------------------------------------

        for match in FREQUENCY_RE.finditer(sentence):
            value = _normalise_frequency(match.group(0))

            facts.append(
                ClinicalFact(
                    category="frequency",
                    value=value,
                    evidence=sentence,
                )
            )

        # -----------------------------------------------------------------
        # Laterality
        # -----------------------------------------------------------------

        for match in LATERALITY_RE.finditer(sentence):
            facts.append(
                ClinicalFact(
                    category="laterality",
                    value=_normalise_laterality(match.group(0)),
                    evidence=sentence,
                )
            )

    # ---------------------------------------------------------------------
    # Deduplicate
    # ---------------------------------------------------------------------
    #
    # Preserve insertion order while removing exact duplicate
    # category/value/evidence triples.
    # ---------------------------------------------------------------------

    seen = set()
    deduped: List[ClinicalFact] = []

    for fact in facts:
        key = (
            fact.category,
            fact.value,
            fact.evidence,
        )

        if key in seen:
            continue

        seen.add(key)
        deduped.append(fact)

    return deduped