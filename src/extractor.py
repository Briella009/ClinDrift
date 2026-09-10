import re
from dataclasses import dataclass, asdict
from typing import List, Dict


@dataclass
class ClinicalFact:
    category: str
    value: str
    evidence: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


NUMBER_WORDS = {
    "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
    "eleven": "11", "twelve": "12",
}
NUM_TOKEN = r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"

DOSAGE_RE = re.compile(r"\b\d+(?:\.\d+)?\s?(?:mg|mcg|g|ml|units?)\b", re.I)
BP_RE = re.compile(r"\b(?:[89]\d|1\d\d|2[0-4]\d)\s*/\s*(?:[4-9]\d|1\d\d)\b")
DURATION_RE = re.compile(rf"\b({NUM_TOKEN})\s+(hours?|days?|weeks?|months?|years?)\b", re.I)
FREQUENCY_RE = re.compile(
    r"\b(?:once|twice|three times|four times)\s+(?:a|per)\s+day\b|"
    r"\b(?:once|twice|three times|four times)\s+daily\b|"
    r"\bonce\s+a\s+week\b|"
    r"\beach\s+(?:night|morning|evening)\b|"
    r"\b(?:daily|weekly|nightly|morning|evening)\b",
    re.I,
)
LATERALITY_RE = re.compile(r"\b(?:left|right|bilateral)\b", re.I)

MEDICATION_HINTS = {
    "metformin", "penicillin", "amoxicillin", "aspirin", "ibuprofen",
    "paracetamol", "acetaminophen", "lisinopril", "amlodipine", "warfarin",
    "insulin", "atorvastatin", "omeprazole",
}

ALLERGY_PATTERNS = [
    re.compile(r"\ballergic to\s+([a-zA-Z0-9\- ]+)", re.I),
    re.compile(r"\b([a-zA-Z0-9\-]+)\s+allergy\b", re.I),
]

NEGATION_PATTERNS = [
    re.compile(r"\bno known (?:drug )?allerg(?:y|ies)\b", re.I),
    re.compile(r"\bdenies\s+([^.,;]+)", re.I),
    re.compile(r"\bno history of\s+([^.,;]+)", re.I),
    re.compile(r"\bnot taking\s+([^.,;]+)", re.I),
]


def _sentences(text: str) -> List[str]:
    chunks = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [c.strip() for c in chunks if c.strip()]


def _canonical_duration(match: re.Match) -> str:
    number = match.group(1).lower()
    unit = match.group(2).lower()
    number = NUMBER_WORDS.get(number, number)
    if number == "1" and unit.endswith("s"):
        unit = unit[:-1]
    elif number != "1" and not unit.endswith("s"):
        unit += "s"
    return f"{number} {unit}"


def _canonical_frequency(raw: str) -> str:
    value = re.sub(r"\s+", " ", raw.strip().lower())
    mapping = {
        "once a day": "once a day",
        "once per day": "once a day",
        "daily": "once a day",
        "once daily": "once a day",
        "twice a day": "twice a day",
        "twice per day": "twice a day",
        "twice daily": "twice a day",
        "three times a day": "three times a day",
        "three times per day": "three times a day",
        "three times daily": "three times a day",
        "four times a day": "four times a day",
        "four times per day": "four times a day",
        "four times daily": "four times a day",
        "weekly": "weekly",
        "once a week": "weekly",
        "nightly": "nightly",
        "each night": "nightly",
        "morning": "morning",
        "each morning": "morning",
        "evening": "evening",
        "each evening": "evening",
    }
    return mapping.get(value, value)


def extract_facts(text: str) -> List[ClinicalFact]:
    facts: List[ClinicalFact] = []

    for sentence in _sentences(text):
        lower = sentence.lower()

        allergy_context = "allerg" in lower
        for med in sorted(MEDICATION_HINTS):
            if re.search(rf"\b{re.escape(med)}\b", lower):
                # Do not treat a drug named only as an allergen as an active medication.
                if allergy_context:
                    continue
                facts.append(ClinicalFact("medication", med, sentence))

        for pattern in ALLERGY_PATTERNS:
            match = pattern.search(sentence)
            if match:
                value = match.group(1).strip(" .,:;")
                facts.append(ClinicalFact("allergy", value.lower(), sentence))

        for pattern in NEGATION_PATTERNS:
            match = pattern.search(sentence)
            if match:
                value = match.group(0).strip()
                facts.append(ClinicalFact("negation", value.lower(), sentence))

        for match in DOSAGE_RE.finditer(sentence):
            facts.append(ClinicalFact("dosage", match.group(0).lower().replace(" ", ""), sentence))

        for match in BP_RE.finditer(sentence):
            facts.append(ClinicalFact("measurement", match.group(0).replace(" ", ""), sentence))

        for match in DURATION_RE.finditer(sentence):
            facts.append(ClinicalFact("duration", _canonical_duration(match), sentence))

        for match in FREQUENCY_RE.finditer(sentence):
            facts.append(ClinicalFact("frequency", _canonical_frequency(match.group(0)), sentence))

        for match in LATERALITY_RE.finditer(sentence):
            facts.append(ClinicalFact("laterality", match.group(0).lower(), sentence))

    # Deduplicate identical category/value/evidence triples while preserving order.
    seen = set()
    deduped = []
    for fact in facts:
        key = (fact.category, fact.value, fact.evidence)
        if key not in seen:
            seen.add(key)
            deduped.append(fact)
    return deduped
