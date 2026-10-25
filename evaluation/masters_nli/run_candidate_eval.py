"""Run one local NLI candidate against a frozen JSONL benchmark."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from nli_adapter import (
    LocalNLIModel,
    classification_summary,
    read_jsonl,
    sha256_file,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    rows = read_jsonl(dataset_path)
    model = LocalNLIModel(args.model)

    predictions = [
        model.predict(row["premise"], row["hypothesis"])
        for row in rows
    ]

    summary = classification_summary(rows, predictions)
    payload = {
        "model": args.model,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": str(dataset_path),
        "dataset_sha256": sha256_file(dataset_path),
        "case_count": len(rows),
        "summary": summary,
        "predictions": [
            {
                "id": row["id"],
                "gold_label": row["label"],
                **prediction,
            }
            for row, prediction in zip(rows, predictions)
        ],
        "reporting_boundary": (
            "Research evaluation only. Results do not establish clinical "
            "validation, medical-device performance, or hospital readiness."
        ),
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
