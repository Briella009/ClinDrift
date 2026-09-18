import json
from pathlib import Path

import pytest

from evaluation.masters_nli.freeze_benchmark import freeze


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )


def nli_case(case_id: str, *, status: str = "agreed") -> dict:
    return {
        "id": case_id,
        "premise": "Patient takes metformin 500 mg.",
        "hypothesis": f"Patient takes metformin {case_id} mg.",
        "label": "contradiction",
        "drift_category": "dosage",
        "scenario_family": "medication_dose",
        "template_family": "dose_template_b",
        "severity": "Critical",
        "meaning_preserving_control": False,
        "provenance": "synthetic",
        "annotation_rationale": "Explicit dose conflict.",
        "independent_check_label": "contradiction",
        "adjudication_status": status,
        "split": "heldout",
        "construction_version": "1",
    }


def test_final_freeze_rejects_pending_adjudication(tmp_path):
    dataset = tmp_path / "heldout.jsonl"
    write_jsonl(dataset, [nli_case("1000", status="pending")])

    with pytest.raises(ValueError, match="pending adjudication"):
        freeze(dataset, mode="nli", final=True)


def test_freeze_rejects_duplicate_ids(tmp_path):
    dataset = tmp_path / "heldout.jsonl"
    row = nli_case("1000")
    second = dict(row)
    second["hypothesis"] = "Patient takes metformin 750 mg."

    write_jsonl(dataset, [row, second])

    with pytest.raises(ValueError, match="Duplicate case ids"):
        freeze(dataset, mode="nli", final=True)


def test_freeze_rejects_development_pair_overlap(tmp_path):
    heldout = tmp_path / "heldout.jsonl"
    development = tmp_path / "development.jsonl"
    row = nli_case("1000")

    write_jsonl(heldout, [row])
    write_jsonl(development, [row])

    with pytest.raises(ValueError, match="overlaps development data"):
        freeze(
            heldout,
            mode="nli",
            final=True,
            development_path=development,
        )


def test_valid_final_freeze_returns_hash_and_counts(tmp_path):
    dataset = tmp_path / "heldout.jsonl"
    write_jsonl(dataset, [nli_case("1000"), nli_case("750")])

    manifest = freeze(dataset, mode="nli", final=True)

    assert manifest["case_count"] == 2
    assert len(manifest["sha256"]) == 64
    assert manifest["summary"]["labels"]["contradiction"] == 2
