from src.evidence_pairing import (
    bidirectional_pairing,
    pairing_recall_at_k,
    retrieve_candidates,
    split_units,
)


def test_split_units_handles_sentences_and_newlines():
    units = split_units("First sentence. Second sentence!\nThird sentence")
    assert units == ["First sentence.", "Second sentence!", "Third sentence"]


def test_lexical_pairing_retrieves_related_medication_sentence():
    source = [
        "Patient takes metformin 500 mg twice daily.",
        "Patient reports headache for three days.",
    ]
    transformed = [
        "The patient takes metformin 1000 mg twice daily.",
    ]

    pairs = retrieve_candidates(
        transformed,
        source,
        direction="transformed_to_source",
        top_k=1,
    )

    assert len(pairs) == 1
    assert pairs[0].candidate_index == 0


def test_bidirectional_pairing_includes_source_to_transformed_pass():
    result = bidirectional_pairing(
        "Patient is allergic to penicillin. Headache for three days.",
        "The patient has headache for three days.",
        top_k=1,
    )

    assert result["transformed_to_source"]
    assert result["source_to_transformed"]

    # The omitted allergy remains a source-side query that can be evaluated
    # for preservation against the transformed document.
    source_queries = {
        item.query_text
        for item in result["source_to_transformed"]
    }
    assert "Patient is allergic to penicillin." in source_queries


def test_pairing_recall_at_k_uses_required_pair_indices():
    pairs = retrieve_candidates(
        ["metformin 1000 mg", "headache three days"],
        ["metformin 500 mg", "headache 3 days"],
        direction="transformed_to_source",
        top_k=1,
    )

    recall = pairing_recall_at_k(
        pairs,
        gold_pairs={(0, 0), (1, 1)},
    )
    assert recall == 1.0


def test_pairing_recall_empty_gold_is_defined_as_one():
    assert pairing_recall_at_k([], []) == 1.0
