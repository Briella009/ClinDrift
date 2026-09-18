"""Validate and freeze ClinDrift held-out JSONL benchmarks.

The script intentionally uses only the Python standard library so it can run in
ordinary CI without downloading model dependencies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


NLI_LABELS = {"contradiction", "entailment", "neutral"}
ADJUDICATION = {"pending", "agreed", "adjudicated"}


def _norm(text: str) -> str:
    return " ".join((text or "").lower().split())


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}: invalid JSON on line {line_number}: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}: line {line_number} is not a JSON object")
            rows.append(row)
    if not rows:
        raise ValueError(f"{path}: benchmark is empty")
    return rows


def _require(row: dict, keys: set[str], *, row_id: str) -> None:
    missing = sorted(key for key in keys if key not in row)
    if missing:
        raise ValueError(f"{row_id}: missing required fields {missing}")


def _validate_common(rows: list[dict], *, final: bool) -> None:
    ids = [str(row.get("id", "")) for row in rows]
    if any(not value.strip() for value in ids):
        raise ValueError("Every benchmark row must have a non-empty id")
    duplicates = [key for key, count in Counter(ids).items() if count > 1]
    if duplicates:
        raise ValueError(f"Duplicate case ids: {duplicates}")

    for row in rows:
        row_id = str(row["id"])
        if row.get("provenance") != "synthetic":
            raise ValueError(
                f"{row_id}: primary master's held-out benchmark must be synthetic"
            )
        status = row.get("adjudication_status")
        if status not in ADJUDICATION:
            raise ValueError(f"{row_id}: invalid adjudication_status {status!r}")
        if final and status == "pending":
            raise ValueError(
                f"{row_id}: cannot freeze final benchmark with pending adjudication"
            )
        for key in ("scenario_family", "template_family"):
            if not str(row.get(key, "")).strip():
                raise ValueError(f"{row_id}: {key} must be non-empty")


def validate_nli(rows: list[dict], *, final: bool) -> dict:
    required = {
        "id","premise","hypothesis","label","drift_category","scenario_family",
        "template_family","meaning_preserving_control","provenance",
        "annotation_rationale","adjudication_status","split"
    }
    _validate_common(rows, final=final)

    seen_pairs = set()
    for row in rows:
        row_id = str(row["id"])
        _require(row, required, row_id=row_id)
        if row["split"] != "heldout":
            raise ValueError(f"{row_id}: split must be 'heldout'")
        if row["label"] not in NLI_LABELS:
            raise ValueError(f"{row_id}: invalid NLI label {row['label']!r}")
        if not isinstance(row["meaning_preserving_control"], bool):
            raise ValueError(f"{row_id}: meaning_preserving_control must be boolean")
        if not str(row["premise"]).strip() or not str(row["hypothesis"]).strip():
            raise ValueError(f"{row_id}: premise/hypothesis cannot be empty")

        pair = (_norm(row["premise"]), _norm(row["hypothesis"]))
        if pair in seen_pairs:
            raise ValueError(f"{row_id}: duplicate normalized premise/hypothesis pair")
        seen_pairs.add(pair)

    return {
        "labels": dict(Counter(row["label"] for row in rows)),
        "categories": dict(Counter(row["drift_category"] for row in rows)),
        "scenario_families": dict(Counter(row["scenario_family"] for row in rows)),
        "template_families": dict(Counter(row["template_family"] for row in rows)),
    }


def validate_pairing(rows: list[dict], *, final: bool) -> dict:
    required = {
        "id","source_units","transformed_units","direction","query_index",
        "gold_candidate_indices","drift_category","scenario_family","template_family",
        "provenance","adjudication_status","split"
    }
    _validate_common(rows, final=final)

    for row in rows:
        row_id = str(row["id"])
        _require(row, required, row_id=row_id)
        if row["split"] != "heldout_pairing":
            raise ValueError(f"{row_id}: split must be 'heldout_pairing'")
        if row["direction"] not in {"transformed_to_source","source_to_transformed"}:
            raise ValueError(f"{row_id}: invalid direction")
        source = row["source_units"]
        transformed = row["transformed_units"]
        if not isinstance(source, list) or not source or not all(str(x).strip() for x in source):
            raise ValueError(f"{row_id}: source_units must be non-empty strings")
        if not isinstance(transformed, list) or not transformed or not all(str(x).strip() for x in transformed):
            raise ValueError(f"{row_id}: transformed_units must be non-empty strings")

        query_limit = len(transformed) if row["direction"] == "transformed_to_source" else len(source)
        candidate_limit = len(source) if row["direction"] == "transformed_to_source" else len(transformed)

        query_index = row["query_index"]
        gold = row["gold_candidate_indices"]
        if not isinstance(query_index, int) or not 0 <= query_index < query_limit:
            raise ValueError(f"{row_id}: query_index is out of range")
        if not isinstance(gold, list) or not gold or any(
            not isinstance(index, int) or not 0 <= index < candidate_limit
            for index in gold
        ):
            raise ValueError(f"{row_id}: gold_candidate_indices are invalid")

    return {
        "directions": dict(Counter(row["direction"] for row in rows)),
        "categories": dict(Counter(row["drift_category"] for row in rows)),
        "scenario_families": dict(Counter(row["scenario_family"] for row in rows)),
        "template_families": dict(Counter(row["template_family"] for row in rows)),
    }


def normalized_nli_pairs(rows: list[dict]) -> set[tuple[str, str]]:
    return {(_norm(row.get("premise", "")), _norm(row.get("hypothesis", ""))) for row in rows}


def check_no_development_overlap(heldout: list[dict], development_path: Path | None) -> None:
    if development_path is None:
        return
    development = _load_jsonl(development_path)
    overlap = normalized_nli_pairs(heldout) & normalized_nli_pairs(development)
    if overlap:
        raise ValueError(
            f"Held-out benchmark overlaps development data on {len(overlap)} normalized pair(s)"
        )


def freeze(
    path: Path,
    *,
    mode: str,
    final: bool,
    development_path: Path | None = None,
) -> dict:
    rows = _load_jsonl(path)

    if mode == "nli":
        summary = validate_nli(rows, final=final)
        check_no_development_overlap(rows, development_path)
    elif mode == "pairing":
        summary = validate_pairing(rows, final=final)
    else:
        raise ValueError(f"Unsupported mode: {mode}")

    return {
        "benchmark_file": path.name,
        "mode": mode,
        "case_count": len(rows),
        "sha256": _sha256(path),
        "final_freeze": bool(final),
        "summary": summary,
        "reporting_boundary": (
            "Synthetic controlled benchmark only; not clinical validation, "
            "medical-device performance, hospital readiness or patient-outcome evidence."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--mode", choices=["nli", "pairing"], required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--development")
    parser.add_argument("--final", action="store_true")
    args = parser.parse_args()

    manifest = freeze(
        Path(args.dataset),
        mode=args.mode,
        final=args.final,
        development_path=Path(args.development) if args.development else None,
    )

    out = Path(args.manifest)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
