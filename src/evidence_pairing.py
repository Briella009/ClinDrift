"""Evidence-pairing utilities for the ClinDrift master's semantic layer.

This module provides an inspectable lexical baseline for retrieving candidate
evidence before NLI. Pairing and NLI are deliberately separate so retrieval
errors can be measured independently of inference errors.

The lexical baseline is not assumed to be the final retrieval method. It gives
the study a reproducible comparator before any embedding-based retriever is
considered.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Iterable

from rapidfuzz.fuzz import token_set_ratio


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")


@dataclass(frozen=True)
class EvidenceCandidate:
    query_index: int
    candidate_index: int
    query_text: str
    candidate_text: str
    score: float
    direction: str

    def to_dict(self) -> dict:
        return asdict(self)


def split_units(text: str) -> list[str]:
    """Split short clinical text into non-empty sentence-like review units."""
    return [
        chunk.strip()
        for chunk in _SENTENCE_SPLIT_RE.split((text or "").strip())
        if chunk.strip()
    ]


def lexical_similarity(left: str, right: str) -> float:
    """Return normalized token-set similarity in [0, 1]."""
    if not left.strip() or not right.strip():
        return 0.0
    return float(token_set_ratio(left, right)) / 100.0


def retrieve_candidates(
    query_units: Iterable[str],
    candidate_units: Iterable[str],
    *,
    direction: str,
    top_k: int = 3,
    minimum_score: float = 0.0,
) -> list[EvidenceCandidate]:
    """Retrieve top-k candidate evidence units for each query unit.

    The function does not decide entailment/contradiction. It only proposes
    evidence pairs for a later NLI stage.
    """
    queries = list(query_units)
    candidates = list(candidate_units)

    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    output: list[EvidenceCandidate] = []

    for query_index, query in enumerate(queries):
        ranked = sorted(
            (
                (
                    candidate_index,
                    candidate,
                    lexical_similarity(query, candidate),
                )
                for candidate_index, candidate in enumerate(candidates)
            ),
            key=lambda item: item[2],
            reverse=True,
        )

        accepted = 0
        for candidate_index, candidate, score in ranked:
            if score < minimum_score:
                continue
            output.append(
                EvidenceCandidate(
                    query_index=query_index,
                    candidate_index=candidate_index,
                    query_text=query,
                    candidate_text=candidate,
                    score=score,
                    direction=direction,
                )
            )
            accepted += 1
            if accepted >= top_k:
                break

    return output


def bidirectional_pairing(
    source_text: str,
    transformed_text: str,
    *,
    top_k: int = 3,
    minimum_score: float = 0.0,
) -> dict[str, list[EvidenceCandidate]]:
    """Return transformed->source and source->transformed candidate pairs."""
    source_units = split_units(source_text)
    transformed_units = split_units(transformed_text)

    return {
        "transformed_to_source": retrieve_candidates(
            transformed_units,
            source_units,
            direction="transformed_to_source",
            top_k=top_k,
            minimum_score=minimum_score,
        ),
        "source_to_transformed": retrieve_candidates(
            source_units,
            transformed_units,
            direction="source_to_transformed",
            top_k=top_k,
            minimum_score=minimum_score,
        ),
    }


def pairing_recall_at_k(
    retrieved: Iterable[EvidenceCandidate],
    gold_pairs: Iterable[tuple[int, int]],
) -> float:
    """Case-level recall for required query/candidate index pairs."""
    gold = set(gold_pairs)
    if not gold:
        return 1.0

    found = {
        (item.query_index, item.candidate_index)
        for item in retrieved
    }
    return len(gold & found) / len(gold)
