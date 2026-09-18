from src.decision_fusion import reconcile


def test_rule_finding_is_never_overridden():
    result = reconcile(
        deterministic_positive=True,
        nli_label="entailment",
        nli_confidence=0.95,
    )
    assert result.final_status == "finding"
    assert result.requires_review
    assert result.mechanism == "deterministic_with_ai_discordance"


def test_ai_can_create_separate_semantic_finding():
    result = reconcile(
        deterministic_positive=False,
        nli_label="contradiction",
        nli_confidence=0.91,
        contradiction_threshold=0.80,
    )
    assert result.final_status == "finding"
    assert result.mechanism == "ai_semantic"


def test_low_confidence_contradiction_abstains():
    result = reconcile(
        deterministic_positive=False,
        nli_label="contradiction",
        nli_confidence=0.55,
        contradiction_threshold=0.80,
    )
    assert result.final_status == "uncertain"
    assert result.mechanism == "ai_abstention"


def test_equivalence_vs_ai_contradiction_is_discordance():
    result = reconcile(
        deterministic_positive=False,
        deterministic_equivalent=True,
        nli_label="contradiction",
        nli_confidence=0.93,
    )
    assert result.final_status == "discordance"
    assert result.requires_review
