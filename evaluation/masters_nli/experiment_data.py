"""Deterministic, disclosed synthetic data construction for an exploratory ClinDrift experiment.

Important: final labels here are author/algorithm constructed, NOT independently
reviewed. The 280-case pilot remains pending adjudication and must not be
represented as an externally validated or final clinical benchmark.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from collections import Counter
from evaluation.icaiae2026.build_and_evaluate import build_cases

SEED = 20261025
VERSION = "masters-synthetic-pilot-v1"
GROUPS = (
    "dose_contradiction", "schedule_contradiction", "laterality_contradiction",
    "pressure_contradiction", "consciousness_contradiction", "symptom_course_contradiction",
    "unsupported_diagnosis", "unsupported_procedure", "omitted_medication",
    "omitted_allergy", "dose_paraphrase_control", "frequency_paraphrase_control",
    "afebrile_paraphrase_control", "unchanged_control",
)
MEDS = ("metformin", "amlodipine", "paracetamol", "atorvastatin", "aspirin",
        "lisinopril", "warfarin", "omeprazole", "amoxicillin", "ibuprofen")
CONDITIONS = ("pneumonia", "asthma", "migraine", "heart failure", "kidney disease",
              "diabetes", "anemia", "sepsis", "arthritis", "depression")
ALLERGENS = ("penicillin", "amoxicillin", "ibuprofen", "aspirin", "latex",
             "iodinated contrast", "cephalexin", "naproxen", "morphine", "sulfa drugs")

def write_jsonl(path: Path, rows: list[dict]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()

def development_cases() -> list[dict]:
    """Existing 140 already-seen examples; model selection/development ONLY."""
    truth = {
        "dosage_drift": "contradiction", "allergy_contradiction": "contradiction",
        "duration_drift": "contradiction", "frequency_drift": "contradiction",
        "measurement_drift": "contradiction", "laterality_drift": "contradiction",
        "semantic_contradiction": "contradiction",
        "omission": "neutral", "supported_addition": "neutral",
        "unsupported_diagnosis": "neutral",
        "unchanged_control": "entailment", "formatting_control": "entailment",
        "duration_paraphrase_control": "entailment",
        "frequency_paraphrase_control": "entailment",
    }
    out = []
    for i, c in enumerate(build_cases()):
        group = c["group"]
        if group not in truth:
            raise ValueError(f"Unmapped existing group {group}")
        reverse = group == "omission"
        premise = c["transformed"] if reverse else c["source"]
        hypo = c["source"] if reverse else c["transformed"]
        out.append({
            "id": c["id"], "premise": premise, "hypothesis": hypo,
            "source_text": c["source"], "transformed_text": c["transformed"],
            "label": truth[group], "drift_category": group,
            "severity": ("Critical" if group in
                         {"allergy_contradiction", "dosage_drift"} else "Medium"),
            "direction": "source_to_transformed" if reverse else "transformed_to_source",
            "integrity_error": bool(c["positive"]),
            "meaning_preserving_control": not bool(c["positive"]),
            "scenario_family": "development_existing_" + group,
            "template_family": "historical_140_" + group,
            "provenance": "synthetic",
            "annotation_rationale": "Existing constructed case label; reinterpreted as directional NLI relation, without independent expert annotation.",
            "adjudication_status": "pending",
            "split": "development",
            "construction_version": "historical-140-derived-v1",
        })
    assert len(out) == 140
    return out

def construct_pair(group: str, i: int) -> tuple[str, str, str, bool, str]:
    """Core source/target sentences, oracle class, ground-truth integrity, direction."""
    med = MEDS[i % len(MEDS)]
    dose_a = (5, 10, 20, 25, 50, 75, 100, 250, 500, 750)[i % 10]
    dose_b = dose_a * 2
    v = i + 200
    if group == "dose_contradiction":
        return (f"For simulated encounter {v}, the prescribed dose of {med} is {dose_a} mg.",
                f"For simulated encounter {v}, the prescribed dose of {med} is {dose_b} mg.",
                "contradiction", True, "transformed_to_source")
    if group == "schedule_contradiction":
        return (f"For simulated encounter {v}, {med} is prescribed exclusively in the morning.",
                f"For simulated encounter {v}, {med} is prescribed exclusively in the evening.",
                "contradiction", True, "transformed_to_source")
    if group == "laterality_contradiction":
        part = ("wrist", "ankle", "shoulder", "elbow", "knee")[i%5]
        return (f"In simulated encounter {v}, tenderness is restricted to the left {part}.",
                f"In simulated encounter {v}, tenderness is restricted to the right {part}.",
                "contradiction", True, "transformed_to_source")
    if group == "pressure_contradiction":
        return (f"In simulated encounter {v}, blood pressure measures {110+i}/72 mmHg.",
                f"In simulated encounter {v}, blood pressure measures {150+i}/96 mmHg.",
                "contradiction", True, "transformed_to_source")
    if group == "consciousness_contradiction":
        return (f"At simulated examination {v}, the patient is fully conscious and responsive.",
                f"At simulated examination {v}, the patient is unconscious and unresponsive.",
                "contradiction", True, "transformed_to_source")
    if group == "symptom_course_contradiction":
        symptom = ("cough","nausea","headache","dizziness","fatigue")[i%5]
        return (f"At simulated follow-up {v}, the {symptom} has completely resolved.",
                f"At simulated follow-up {v}, the {symptom} has persisted without improvement.",
                "contradiction", True, "transformed_to_source")
    if group == "unsupported_diagnosis":
        cond = CONDITIONS[i%10]
        return (f"At simulated intake {v}, the patient reports intermittent calf pain.",
                f"At simulated intake {v}, the clinician diagnosed {cond}.",
                "neutral", True, "transformed_to_source")
    if group == "unsupported_procedure":
        procedure = ("MRI", "CT scan", "endoscopy", "ultrasound", "ECG")[i%5]
        return (f"At simulated visit {v}, the patient describes mild ankle discomfort.",
                f"At simulated visit {v}, a {procedure} was performed.",
                "neutral", True, "transformed_to_source")
    if group == "omitted_medication":
        return (f"At simulated review {v}, the medication list includes {med} at {dose_a} mg.",
                f"At simulated review {v}, the clinician documents intermittent shoulder stiffness.",
                "neutral", True, "source_to_transformed")
    if group == "omitted_allergy":
        allergen = ALLERGENS[i%10]
        return (f"At simulated review {v}, the allergy list records sensitivity to {allergen}.",
                f"At simulated review {v}, the patient describes occasional ankle swelling.",
                "neutral", True, "source_to_transformed")
    if group == "dose_paraphrase_control":
        return (f"For simulated encounter {v}, {med} is scheduled at {dose_a} mg daily.",
                f"For simulated encounter {v}, the daily {med} dose is {dose_a} mg.",
                "entailment", False, "transformed_to_source")
    if group == "frequency_paraphrase_control":
        return (f"During simulated visit {v}, {med} is taken once every day.",
                f"During simulated visit {v}, {med} is taken daily.",
                "entailment", False, "transformed_to_source")
    if group == "afebrile_paraphrase_control":
        return (f"At simulated check {v}, the person does not have a fever.",
                f"At simulated check {v}, the person is afebrile.",
                "entailment", False, "transformed_to_source")
    if group == "unchanged_control":
        return (f"During simulated appointment {v}, respiratory rate is {14+i} breaths per minute.",
                f"During simulated appointment {v}, respiratory rate is {14+i} breaths per minute.",
                "entailment", False, "transformed_to_source")
    raise ValueError(group)

def synthetic_pilot() -> list[dict]:
    """Separate 280-case synthetic pilot; labels await human adjudication."""
    out = []
    context1 = "This record is for a simulated training appointment."
    context2 = "The clinic visit was documented in a test environment."
    for group in GROUPS:
        for i in range(20):
            src, trans, label, is_error, direction = construct_pair(group,i)
            # Three sentence-like units in each document, core evidence always at index 0.
            src_doc = " ".join([src, context1, context2])
            trans_doc = " ".join([trans, context1, context2])
            premise = trans if direction=="source_to_transformed" else src
            hypo = src if direction=="source_to_transformed" else trans
            case_id = f"CD-HOLD-{len(out)+1:03d}"
            out.append({
                "id":case_id,
                "premise":premise, "hypothesis":hypo,
                "source_text":src_doc, "transformed_text":trans_doc,
                "label":label, "direction":direction,
                "integrity_error":is_error, "meaning_preserving_control":not is_error,
                "severity":"Critical" if group in ("dose_contradiction","consciousness_contradiction","omitted_allergy") else "Medium",
                "drift_category":group,
                "scenario_family":"new_synthetic_"+group,
                "template_family":"new_pilot_v1_"+group,
                "provenance":"synthetic",
                "construction_version":VERSION,
                "annotation_rationale":"Programmatically specified source/target mutation; requires human label review and domain judgement.",
                "independent_check_label":None,
                "adjudication_status":"pending",
                "split":"heldout",
                "gold_query_index":0,
                "gold_candidate_indices":[0],
                "synthetic_review_status":"unreviewed",
            })
    assert len(out)==280
    norms = [(" ".join(x["premise"].lower().split())," ".join(x["hypothesis"].lower().split())) for x in out]
    if len(norms)!=len(set(norms)): raise ValueError("Duplicate oracle NLI pairs")
    return out

def verify_disjoint(dev: list[dict], new: list[dict]) -> dict:
    norm = lambda r: (" ".join(r["premise"].lower().split())," ".join(r["hypothesis"].lower().split()))
    intersection = {norm(r) for r in dev} & {norm(r) for r in new}
    common_families = {r["template_family"] for r in dev} & {r["template_family"] for r in new}
    if intersection or common_families:
        raise ValueError(f"Development overlap: {len(intersection)} pairs, {common_families} families")
    return {"exact_normalized_pair_overlap":0,"template_family_id_overlap":0,
            "warning":"Different declared family IDs do not prove semantic/template independence."}

if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="experiment_outputs")
    a=parser.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    dev=development_cases(); hold=synthetic_pilot()
    audit=verify_disjoint(dev,hold)
    hashes={"development":write_jsonl(out/"development_140_derived_nli.jsonl",dev),
            "heldout_pilot":write_jsonl(out/"synthetic_heldout_pilot_280.jsonl",hold)}
    print(json.dumps({"n_dev":len(dev),"n_pilot":len(hold),
       "dev_labels":dict(Counter(x["label"] for x in dev)),
       "heldout_labels":dict(Counter(x["label"] for x in hold)),
       "hashes":hashes, "overlap_checks":audit},indent=2))
