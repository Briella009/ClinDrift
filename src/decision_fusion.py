"""Decision-fusion rules for the proposed hybrid ClinDrift architecture.

This module is deliberately model-agnostic. It reconciles an optional deterministic
finding with an NLI semantic decision while preserving provenance. It does not claim
clinical risk or replace human review.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class FusionDecision:
    final_status: str
    mechanism: str
    requires_review: bool
    rationale: str

    def to_dict(self) -> dict:
        return asdict(self)


def reconcile(
    *,
    deterministic_positive: bool,
    deterministic_equivalent: bool = False,
    nli_label: Optional[str] = None,
    nli_confidence: Optional[float] = None,
    contradiction_threshold: float = 0.80,
) -> FusionDecision:
    """Apply conservative rule-AI reconciliation.

    Expected nli_label values: contradiction, entailment, neutral, or None.
    """

    label = (nli_label or "none").lower()
    confidence = float(nli_confidence or 0.0)

    if deterministic_positive:
        if label == "contradiction" and confidence >= contradiction_threshold:
            return FusionDecision(
                final_status="finding",
                mechanism="deterministic+ai_corroborated",
                requires_review=True,
                rationale=(
                    "The deterministic finding is retained and the AI layer "
                    "independently corroborates a contradiction."
                ),
            )
        return FusionDecision(
            final_status="finding",
            mechanism="deterministic_with_ai_discordance",
            requires_review=True,
            rationale=(
                "The deterministic finding is retained. AI uncertainty or "
                "disagreement is recorded rather than overriding direct rule evidence."
            ),
        )

    if deterministic_equivalent and label == "contradiction":
        return FusionDecision(
            final_status="discordance",
            mechanism="rule_ai_discordance",
            requires_review=True,
            rationale=(
                "The deterministic layer considers the expressions equivalent while "
                "the AI layer predicts contradiction; the conflict is escalated."
            ),
        )

    if label == "contradiction" and confidence >= contradiction_threshold:
        return FusionDecision(
            final_status="finding",
            mechanism="ai_semantic",
            requires_review=True,
            rationale=(
                "No supported deterministic rule fired, but the NLI layer produced "
                "a high-confidence contradiction. The finding remains separately "
                "labelled as AI-derived."
            ),
        )

    if label in {"neutral", "contradiction"}:
        return FusionDecision(
            final_status="uncertain",
            mechanism="ai_abstention",
            requires_review=True,
            rationale=(
                "The available semantic evidence is not strong enough for an "
                "automated integrity finding. The system abstains and preserves the "
                "case for review."
            ),
        )

    return FusionDecision(
        final_status="no_automated_finding",
        mechanism="no_issue_detected",
        requires_review=False,
        rationale=(
            "Neither the deterministic layer nor the semantic layer produced a "
            "supported integrity finding."
        ),
    )
