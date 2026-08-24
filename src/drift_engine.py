from dataclasses import dataclass, asdict
from typing import List, Dict
from rapidfuzz.fuzz import ratio

from .extractor import ClinicalFact


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


CRITICAL_CATEGORIES = {"allergy", "dosage", "measurement", "negation"}
HIGH_CATEGORIES = {"medication", "frequency", "laterality", "duration"}
DIRECT_COMPARE_CATEGORIES = {"dosage", "duration", "frequency", "laterality", "measurement"}


def _severity(category: str) -> str:
    if category in CRITICAL_CATEGORIES:
        return "Critical"
    if category in HIGH_CATEGORIES:
        return "High"
    return "Medium"


def _group(facts: List[ClinicalFact]):
    grouped = {}
    for fact in facts:
        grouped.setdefault(fact.category, []).append(fact)
    return grouped


def _best_similarity(value: str, candidates: List[ClinicalFact]) -> float:
    if not candidates:
        return 0.0
    return max(ratio(value.lower(), c.value.lower()) for c in candidates)


def _add(findings, drift_type, category, source_value, transformed_value,
         source_evidence, transformed_evidence, rationale, severity=None):
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


def compare_facts(source: List[ClinicalFact], transformed: List[ClinicalFact]) -> List[DriftFinding]:
    findings: List[DriftFinding] = []
    sgroup = _group(source)
    tgroup = _group(transformed)

    # Explicit allergy contradiction: a recorded allergy becomes "no known allergies".
    s_allergies = sgroup.get("allergy", [])
    t_allergies = tgroup.get("allergy", [])
    s_negations = sgroup.get("negation", [])
    t_negations = tgroup.get("negation", [])

    t_no_allergy = next((n for n in t_negations if "allerg" in n.value and "no known" in n.value), None)
    s_no_allergy = next((n for n in s_negations if "allerg" in n.value and "no known" in n.value), None)

    handled_source_allergies = set()
    handled_transformed_allergies = set()
    handled_source_negations = set()
    handled_transformed_negations = set()

    if s_allergies and t_no_allergy:
        for sf in s_allergies:
            _add(
                findings,
                "Allergy contradiction",
                "allergy",
                sf.value,
                t_no_allergy.value,
                sf.evidence,
                t_no_allergy.evidence,
                "A documented allergy was transformed into a statement indicating no known allergies.",
                severity="Critical",
            )
            handled_source_allergies.add(id(sf))
        handled_transformed_negations.add(id(t_no_allergy))

    if s_no_allergy and t_allergies:
        for tf in t_allergies:
            _add(
                findings,
                "Allergy contradiction",
                "allergy",
                s_no_allergy.value,
                tf.value,
                s_no_allergy.evidence,
                tf.evidence,
                "The source indicates no known allergies, but the transformed text introduces an allergy.",
                severity="Critical",
            )
            handled_transformed_allergies.add(id(tf))
        handled_source_negations.add(id(s_no_allergy))

    categories = sorted(set(sgroup) | set(tgroup))

    for category in categories:
        sitems = sgroup.get(category, [])
        titems = tgroup.get(category, [])

        if category == "allergy":
            sitems = [x for x in sitems if id(x) not in handled_source_allergies]
            titems = [x for x in titems if id(x) not in handled_transformed_allergies]
        elif category == "negation":
            sitems = [x for x in sitems if id(x) not in handled_source_negations]
            titems = [x for x in titems if id(x) not in handled_transformed_negations]

        # Numeric/temporal/laterality fields are directly comparable when each side has one value.
        if category in DIRECT_COMPARE_CATEGORIES and len(sitems) == 1 and len(titems) == 1:
            sf, tf = sitems[0], titems[0]
            if sf.value.lower() != tf.value.lower():
                _add(
                    findings,
                    f"{category.title()} drift",
                    category,
                    sf.value,
                    tf.value,
                    sf.evidence,
                    tf.evidence,
                    f"The {category} value changed during transformation.",
                )
            continue

        # Source facts absent from transformed text: omission candidates.
        for sf in sitems:
            similarity = _best_similarity(sf.value, titems)
            if not titems or similarity < 55:
                _add(
                    findings,
                    "Omission",
                    category,
                    sf.value,
                    "—",
                    sf.evidence,
                    "—",
                    f"Source {category} fact is not preserved in the transformed text.",
                )

        # New facts in transformed text absent from source: unsupported additions.
        for tf in titems:
            similarity = _best_similarity(tf.value, sitems)
            if not sitems or similarity < 55:
                _add(
                    findings,
                    "Unsupported addition",
                    category,
                    "—",
                    tf.value,
                    "—",
                    tf.evidence,
                    f"Transformed text introduces a {category} fact not found in the source.",
                )

        # Same category but materially changed values: drift candidates.
        if sitems and titems:
            for sf in sitems:
                ranked = sorted(titems, key=lambda x: ratio(sf.value.lower(), x.value.lower()), reverse=True)
                tf = ranked[0]
                similarity = ratio(sf.value.lower(), tf.value.lower())
                if 55 <= similarity < 100 and sf.value.lower() != tf.value.lower():
                    _add(
                        findings,
                        f"{category.title()} drift",
                        category,
                        sf.value,
                        tf.value,
                        sf.evidence,
                        tf.evidence,
                        f"The {category} value changed during transformation.",
                    )

    # Remove duplicate findings.
    unique = []
    seen = set()
    for item in findings:
        key = (
            item.drift_type,
            item.source_value,
            item.transformed_value,
            item.source_evidence,
            item.transformed_evidence,
        )
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique
