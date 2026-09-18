"""Utilities for local NLI candidate evaluation.

The module keeps Transformers imports lazy so the ordinary ClinDrift test suite
can run without downloading AI-model dependencies.
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
import time
from pathlib import Path
from typing import Iterable


LABELS = ("contradiction", "entailment", "neutral")


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_calibration_error(
    confidences: Iterable[float],
    correct: Iterable[bool],
    bins: int = 10,
) -> float:
    """Return simple top-label ECE in [0, 1]."""
    confidences = list(confidences)
    correct = list(correct)
    if len(confidences) != len(correct):
        raise ValueError("confidences and correct must have equal length")
    if not confidences:
        return 0.0

    total = len(confidences)
    ece = 0.0
    for index in range(bins):
        lower = index / bins
        upper = (index + 1) / bins
        members = [
            i
            for i, value in enumerate(confidences)
            if (lower <= value < upper) or (index == bins - 1 and value == 1.0)
        ]
        if not members:
            continue
        mean_conf = sum(confidences[i] for i in members) / len(members)
        mean_acc = sum(bool(correct[i]) for i in members) / len(members)
        ece += (len(members) / total) * abs(mean_acc - mean_conf)
    return ece


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    if not 0 <= q <= 1:
        raise ValueError("q must be between 0 and 1")
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return ordered[low]
    weight = position - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


class LocalNLIModel:
    """Thin local inference wrapper around a Hugging Face sequence classifier."""

    def __init__(self, model_name: str):
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        import torch

        self.torch = torch
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()

        raw_map = {
            int(key): str(value).lower()
            for key, value in self.model.config.id2label.items()
        }
        self.id2label = raw_map

    def predict(self, premise: str, hypothesis: str) -> dict:
        encoded = self.tokenizer(
            premise,
            hypothesis,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        started = time.perf_counter()
        with self.torch.inference_mode():
            logits = self.model(**encoded).logits[0]
            probs = self.torch.softmax(logits, dim=-1).cpu().tolist()
        elapsed_ms = (time.perf_counter() - started) * 1000

        scores = {
            self.id2label[index]: float(probability)
            for index, probability in enumerate(probs)
        }
        label = max(scores, key=scores.get)
        return {
            "label": label,
            "confidence": scores[label],
            "scores": scores,
            "latency_ms": elapsed_ms,
        }


def read_jsonl(path: str | Path) -> list[dict]:
    rows = []
    with open(path, "r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            required = {"id", "premise", "hypothesis", "label"}
            missing = required - set(row)
            if missing:
                raise ValueError(
                    f"Line {line_number} missing required fields: {sorted(missing)}"
                )
            if row["label"] not in LABELS:
                raise ValueError(
                    f"Line {line_number} has unsupported label {row['label']!r}"
                )
            rows.append(row)
    return rows


def _multiclass_brier_score(rows: list[dict], predictions: list[dict]) -> float:
    """Mean multiclass Brier score across the three NLI labels."""
    if not rows:
        return 0.0
    total = 0.0
    for row, prediction in zip(rows, predictions):
        scores = prediction.get("scores", {})
        for label in LABELS:
            target = 1.0 if row["label"] == label else 0.0
            total += (float(scores.get(label, 0.0)) - target) ** 2
    return total / len(rows)


def _negative_log_likelihood(rows: list[dict], predictions: list[dict]) -> float:
    """Mean negative log likelihood for the gold NLI label."""
    if not rows:
        return 0.0
    epsilon = 1e-12
    losses = []
    for row, prediction in zip(rows, predictions):
        probability = float(prediction.get("scores", {}).get(row["label"], 0.0))
        losses.append(-math.log(max(probability, epsilon)))
    return sum(losses) / len(losses)


def classification_summary(rows: list[dict], predictions: list[dict]) -> dict:
    from sklearn.metrics import (
        accuracy_score,
        confusion_matrix,
        precision_recall_fscore_support,
    )

    truth = [row["label"] for row in rows]
    predicted = [item["label"] for item in predictions]
    confidence = [item["confidence"] for item in predictions]
    correct = [a == b for a, b in zip(truth, predicted)]

    precision, recall, f1, support = precision_recall_fscore_support(
        truth,
        predicted,
        labels=list(LABELS),
        zero_division=0,
    )
    macro_precision, macro_recall, macro_f1, _ = precision_recall_fscore_support(
        truth,
        predicted,
        labels=list(LABELS),
        average="macro",
        zero_division=0,
    )

    per_class = {
        label: {
            "precision": float(precision[index]),
            "recall": float(recall[index]),
            "f1": float(f1[index]),
            "support": int(support[index]),
        }
        for index, label in enumerate(LABELS)
    }

    critical_indices = [
        index
        for index, row in enumerate(rows)
        if str(row.get("severity", "")).lower() == "critical"
        and row["label"] == "contradiction"
    ]
    if critical_indices:
        critical_recall = sum(
            predictions[index]["label"] == "contradiction"
            for index in critical_indices
        ) / len(critical_indices)
    else:
        critical_recall = None

    control_indices = [
        index
        for index, row in enumerate(rows)
        if bool(row.get("meaning_preserving_control", False))
    ]
    if control_indices:
        false_positive_rate_controls = sum(
            predictions[index]["label"] == "contradiction"
            for index in control_indices
        ) / len(control_indices)
    else:
        false_positive_rate_controls = None

    latencies = [item["latency_ms"] for item in predictions]

    return {
        "accuracy": float(accuracy_score(truth, predicted)),
        "macro_precision": float(macro_precision),
        "macro_recall": float(macro_recall),
        "macro_f1": float(macro_f1),
        "contradiction_recall": per_class["contradiction"]["recall"],
        "critical_error_recall": critical_recall,
        "false_positive_rate_controls": false_positive_rate_controls,
        "brier_score": _multiclass_brier_score(rows, predictions),
        "negative_log_likelihood": _negative_log_likelihood(rows, predictions),
        "expected_calibration_error": expected_calibration_error(confidence, correct),
        "latency_median_ms": float(statistics.median(latencies)) if latencies else 0.0,
        "latency_p95_ms": float(percentile(latencies, 0.95)),
        "per_class": per_class,
        "confusion_matrix": confusion_matrix(
            truth,
            predicted,
            labels=list(LABELS),
        ).tolist(),
        "label_order": list(LABELS),
    }
