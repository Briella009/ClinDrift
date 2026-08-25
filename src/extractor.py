from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Dict, Iterable, List, Sequence, Tuple


# =============================================================================
# DATA MODEL
# =============================================================================


@dataclass(frozen=True)
class ClinicalFact:
    """
    A single clinical-information fact extracted from text.

    category:
        The type of information extracted, for example:
        medication, allergy, dosage, measurement, duration or frequency.

    value:
        The extracted value used by the comparison engine.

    evidence:
        The original sentence from which the fact was extracted.

    ClinDrift intentionally preserves evidence separately from later semantic
    normalisation so that reviewers can always inspect the original wording.
    """

    category: str
    value: str
    evidence: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


# =============================================================================
# NUMBER EXPRESSIONS
# =============================================================================


# v0.2 expands duration extraction beyond digits.
#
# Examples now supported:
#
#   3 days
#   three days
#   7 days
#   one week
#   twenty days
#
# Comparison equivalence itself is handled by drift_engine.py.

NUMBER_WORD_PATTERN = (
    r"(?:"
    r"zero|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|"
    r"seventeen|eighteen|nineteen|twenty|thirty|forty|"
    r"fifty|sixty|seventy|eighty|ninety"
    r")"
)

NUMBER_OR_DIGIT_PATTERN = rf"(?:\d+|{NUMBER_WORD_PATTERN})"


# =============================================================================
# CORE EXTRACTION PATTERNS
# =============================================================================


DOSAGE_RE = re.compile(
    r"\b"
    r"\d+(?:\.\d+)?"
    r"\s*"
    r"(?:mg|mcg|g|kg|ml|l|units?)"
    r"\b",
    re.IGNORECASE,
)


BP_RE = re.compile(
    r"\b"
    r"(?:[89]\d|1\d\d|2[0-4]\d)"
    r"\s*/\s*"
    r"(?:[4-9]\d|1\d\d)"
    r"\b"
)


DURATION_RE = re.compile(
    rf"\b"
    rf"{NUMBER_OR_DIGIT_PATTERN}"
    rf"\s+"
    rf"(?:hours?|days?|weeks?|months?|years?)"
    rf"\b",
    re.IGNORECASE,
)


# IMPORTANT:
# More specific frequency expressions must appear before generic forms such
# as "daily". This prevents:
#
#     "twice daily"
#
# from being extracted merely as:
#
#     "daily"
#
# That surface-form loss caused one of the ClinDrift v0.1 false positives.

FREQUENCY_RE = re.compile(
    r"\b(?:once|twice|three times|four times)\s+"
    r"(?:(?:a|per)\s+day|daily)\b"
    r"|"
    r"\bevery\s+(?:morning|evening|night|day|week)\b"
    r"|"
    r"\b(?:daily|weekly|nightly|morning|evening)\b",
    re.IGNORECASE,
)


LATERALITY_RE = re.compile(
    r"\b(?:left|right|bilateral)\b",
    re.IGNORECASE,
)


# =============================================================================
# MEDICATION VOCABULARY
# =============================================================================


# This remains intentionally small and transparent for the research prototype.
#
# ClinDrift v0.2 should not pretend this is a comprehensive pharmaceutical
# ontology. A future version can replace or supplement this list with a
# validated terminology source.

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


# =============================================================================
# ALLERGY EXTRACTION
# =============================================================================


# Pattern 1:
#   Patient is allergic to penicillin.
#
# Pattern 2:
#   Patient has a penicillin allergy.
#
# Capture is deliberately stopped before common sentence punctuation.

ALLERGY_PATTERNS: Sequence[re.Pattern[str]] = (
    re.compile(
        r"\ballergic\s+to\s+"
        r"([a-zA-Z0-9][a-zA-Z0-9\- ]*?)"
        r"(?=\s*(?:[.,;!?]|$))",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b"
        r"([a-zA-Z0-9][a-zA-Z0-9\-]*)"
        r"\s+allergy\b",
        re.IGNORECASE,
    ),
)


# =============================================================================
# NEGATION EXTRACTION
# =============================================================================


# General natural-language negation reasoning is deliberately not claimed here.
#
# These are explicit patterns currently supported by the research prototype.
#
# More advanced assertion-polarity detection will be evaluated separately.

NEGATION_PATTERNS: Sequence[re.Pattern[str]] = (
    re.compile(
        r"\bno known (?:drug )?allerg(?:y|ies)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bdenies\s+([^.,;!?]+)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bno history of\s+([^.,;!?]+)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bnot taking\s+([^.,;!?]+)",
        re.IGNORECASE,
    ),
)


# =============================================================================
# TEXT HELPERS
# =============================================================================


def _normalise_space(value: str) -> str:
    """
    Collapse repeated whitespace without changing substantive wording.
    """

    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


def _clean_capture(value: str) -> str:
    """
    Clean punctuation surrounding an extracted fact while preserving the
    original semantic content.
    """

    value = _normalise_space(value)

    return value.strip(
        " .,:;!?()[]{}"
    )


def _sentences(text: str) -> List[str]:
    """
    Lightweight sentence splitter.

    It preserves sentence text because ClinDrift uses the sentence as
    claim-level evidence.

    This is intentionally deterministic and dependency-light.
    """

    if not text:
        return []

    cleaned = text.strip()

    if not cleaned:
        return []

    chunks = re.split(
        r"(?<=[.!?])\s+|\n+",
        cleaned,
    )

    return [
        _normalise_space(chunk)
        for chunk in chunks
        if chunk and chunk.strip()
    ]


# =============================================================================
# ALLERGY HELPERS
# =============================================================================


def _extract_allergies(
    sentence: str,
) -> Tuple[List[ClinicalFact], List[Tuple[int, int]]]:
    """
    Extract allergy facts and return their text spans.

    Returning spans allows medication extraction to avoid treating a drug
    mentioned solely as an allergen as an active medication.

    Example:

        Patient is allergic to penicillin.

    should produce:

        allergy = penicillin

    but should NOT additionally produce:

        medication = penicillin
    """

    facts: List[ClinicalFact] = []
    spans: List[Tuple[int, int]] = []

    for pattern in ALLERGY_PATTERNS:
        for match in pattern.finditer(sentence):
            value = _clean_capture(
                match.group(1)
            ).lower()

            if not value:
                continue

            facts.append(
                ClinicalFact(
                    category="allergy",
                    value=value,
                    evidence=sentence,
                )
            )

            spans.append(
                match.span()
            )

    return facts, spans


def _inside_any_span(
    start: int,
    end: int,
    spans: Iterable[Tuple[int, int]],
) -> bool:
    """
    Return True when the supplied range occurs within any protected span.
    """

    for span_start, span_end in spans:
        if start >= span_start and end <= span_end:
            return True

    return False


# =============================================================================
# EXTRACTION
# =============================================================================


def extract_facts(
    text: str,
) -> List[ClinicalFact]:
    """
    Extract supported clinical facts from free clinical text.

    Design goals:

    1. deterministic behaviour;
    2. transparent extraction;
    3. original evidence preservation;
    4. semantic-equivalence support through richer extraction;
    5. minimal external dependencies;
    6. no claim of comprehensive clinical NLP.

    Semantic normalisation is intentionally handled by drift_engine.py rather
    than rewriting evidence here.
    """

    facts: List[ClinicalFact] = []

    for sentence in _sentences(text):
        lower_sentence = sentence.lower()

        # =====================================================================
        # ALLERGIES
        # =====================================================================

        allergy_facts, allergy_spans = _extract_allergies(
            sentence
        )

        facts.extend(
            allergy_facts
        )

        # =====================================================================
        # NEGATIONS
        # =====================================================================

        for pattern in NEGATION_PATTERNS:
            for match in pattern.finditer(sentence):
                value = _clean_capture(
                    match.group(0)
                ).lower()

                if not value:
                    continue

                facts.append(
                    ClinicalFact(
                        category="negation",
                        value=value,
                        evidence=sentence,
                    )
                )

        # =====================================================================
        # MEDICATIONS
        # =====================================================================

        for medication in sorted(
            MEDICATION_HINTS,
            key=len,
            reverse=True,
        ):
            medication_pattern = re.compile(
                rf"\b{re.escape(medication)}\b",
                re.IGNORECASE,
            )

            for medication_match in medication_pattern.finditer(
                sentence
            ):
                start, end = medication_match.span()

                # If the medication word occurs inside an allergy expression,
                # do not automatically treat it as an active medication.
                if _inside_any_span(
                    start,
                    end,
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

        # =====================================================================
        # DOSAGE
        # =====================================================================

        for match in DOSAGE_RE.finditer(sentence):
            value = (
                match.group(0)
                .lower()
                .replace(" ", "")
            )

            facts.append(
                ClinicalFact(
                    category="dosage",
                    value=value,
                    evidence=sentence,
                )
            )

        # =====================================================================
        # MEASUREMENT
        # =====================================================================

        for match in BP_RE.finditer(sentence):
            value = (
                match.group(0)
                .replace(" ", "")
            )

            facts.append(
                ClinicalFact(
                    category="measurement",
                    value=value,
                    evidence=sentence,
                )
            )

        # =====================================================================
        # DURATION
        # =====================================================================

        for match in DURATION_RE.finditer(sentence):
            value = _normalise_space(
                match.group(0).lower()
            )

            facts.append(
                ClinicalFact(
                    category="duration",
                    value=value,
                    evidence=sentence,
                )
            )

        # =====================================================================
        # FREQUENCY
        # =====================================================================

        for match in FREQUENCY_RE.finditer(sentence):
            value = _normalise_space(
                match.group(0).lower()
            )

            facts.append(
                ClinicalFact(
                    category="frequency",
                    value=value,
                    evidence=sentence,
                )
            )

        # =====================================================================
        # LATERALITY
        # =====================================================================

        for match in LATERALITY_RE.finditer(sentence):
            value = match.group(0).lower()

            facts.append(
                ClinicalFact(
                    category="laterality",
                    value=value,
                    evidence=sentence,
                )
            )

    # =========================================================================
    # DEDUPLICATION
    # =========================================================================

    # Deduplicate exact category/value/evidence triples while preserving order.
    #
    # Importantly, evidence is included in the key. The same clinical fact
    # appearing in two different source sentences remains traceable to both
    # locations rather than being silently collapsed across the document.

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
        deduped.append(
            fact
        )

    return deduped