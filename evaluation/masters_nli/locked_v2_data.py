"""Locked second-wave synthetic benchmark generator (NOT clinician-adjudicated).

Created separately from the model-selection 140 cases and pilot v1.
The construction defines exact case-level ground truth and evidence-location indices.
It is NOT an independent hospital dataset or externally adjudicated test.
"""
from __future__ import annotations
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

SEED = 20261025 + 1907
GROUPS = (
    "no_fever_to_fever", "pain_mild_to_severe", "walks_unaided_to_assisted",
    "wound_dry_to_discharging", "symptom_improving_to_worsening",
    "negative_to_positive_test", "prescription_dose_change",
    "unsupported_diagnosis", "unsupported_procedure", "omitted_allergy",
    "afebrile_paraphrase_control", "evening_timing_paraphrase_control",
    "pressure_format_control", "unchanged_control",
)
DRUGS = ("metformin", "amlodipine", "warfarin", "atorvastatin", "omeprazole",
         "lisinopril", "aspirin", "paracetamol", "ibuprofen", "amoxicillin")
SITES = ("ankle", "knee", "shoulder", "wrist", "hip", "elbow")
SYMPTOMS = ("nausea", "headache", "dizziness", "cough", "fatigue")
TESTS = ("malaria antigen", "influenza antigen", "streptococcal antigen",
         "urine pregnancy", "rapid COVID-19")
CONDITIONS = ("asthma", "pneumonia", "diabetes mellitus", "migraine",
              "heart failure", "rheumatoid arthritis")
PROCEDURES = ("MRI", "CT scan", "gastroscopy", "ultrasound", "electrocardiogram")
ALLERGENS = ("penicillin", "latex", "amoxicillin", "naproxen", "aspirin")
BACKGROUND_TEMPLATES = (
    "The visit was registered as synthetic outpatient encounter {id}.",
    "The patient was offered a printed appointment summary at visit {id}.",
    "A simulated follow-up date was entered in the training calendar for visit {id}.",
    "Routine administrative consent was recorded for practice visit {id}.",
    "The appointment ended with a routine scheduling discussion for visit {id}.",
)
EXPECTED = 280

def core(group: str, i: int, case_id: int):
    med = DRUGS[i % len(DRUGS)]
    site = SITES[i % len(SITES)]
    symptom = SYMPTOMS[i % len(SYMPTOMS)]
    suffix=f" during simulated encounter {case_id}"
    # Each tuple: source claim (possibly None), transformed claim (possibly None),
    # primary relation where both claims exist, and case-level integrity error.
    if group=="no_fever_to_fever":
        return (f"Examination showed no fever{suffix}.",
                f"Examination established that the patient had fever{suffix}.",
                "contradiction", True)
    if group=="pain_mild_to_severe":
        return (f"The {site} pain was mild and did not restrict movement{suffix}.",
                f"The {site} pain was severe and limited movement{suffix}.",
                "contradiction", True)
    if group=="walks_unaided_to_assisted":
        return (f"The patient was able to walk without support{suffix}.",
                f"The patient required physical assistance for walking{suffix}.",
                "contradiction", True)
    if group=="wound_dry_to_discharging":
        return (f"The wound remained completely dry{suffix}.",
                f"The wound showed active fluid discharge{suffix}.",
                "contradiction", True)
    if group=="symptom_improving_to_worsening":
        return (f"The patient's {symptom} had improved since the previous review{suffix}.",
                f"The patient's {symptom} had worsened since the previous review{suffix}.",
                "contradiction", True)
    if group=="negative_to_positive_test":
        assay=TESTS[i%len(TESTS)]
        return (f"The {assay} test result was negative{suffix}.",
                f"The {assay} test result was positive{suffix}.",
                "contradiction", True)
    if group=="prescription_dose_change":
        dose=10*(i%5+1)
        return (f"The patient takes {med} {dose} mg daily{suffix}.",
                f"The patient takes {med} {dose+25} mg daily{suffix}.",
                "contradiction", True)
    if group=="unsupported_diagnosis":
        return (None,f"A diagnosis of {CONDITIONS[i%len(CONDITIONS)]} was entered{suffix}.","neutral",True)
    if group=="unsupported_procedure":
        return (None,f"A {PROCEDURES[i%len(PROCEDURES)]} was performed{suffix}.","neutral",True)
    if group=="omitted_allergy":
        return (f"The chart lists an allergy to {ALLERGENS[i%len(ALLERGENS)]}{suffix}.",None,"neutral",True)
    if group=="afebrile_paraphrase_control":
        return (f"The patient had no fever at triage{suffix}.",
                f"The patient was afebrile at triage{suffix}.","entailment",False)
    if group=="evening_timing_paraphrase_control":
        return (f"The {med} tablet is taken in the evening{suffix}.",
                f"The {med} tablet is taken every evening{suffix}.","entailment",False)
    if group=="pressure_format_control":
        a=120+i%14
        b=72+i%10
        return (f"Blood pressure was {a} / {b} mmHg{suffix}.",
                f"Blood pressure was {a}/{b} mmHg{suffix}.","entailment",False)
    if group=="unchanged_control":
        s=f"At triage, respiratory rate was {14+i%6} breaths per minute{suffix}."
        return (s,s,"entailment",False)
    raise ValueError(group)

def construction():
    out=[]
    for group in GROUPS:
        for j in range(20):
            n=len(out)+1
            source_target, transformed_target, nli_label, error=core(group,j,n)
            fillers=[t.format(id=n) for t in BACKGROUND_TEMPLATES]
            source=list(fillers); transformed=list(fillers)
            if source_target: source.append(source_target)
            if transformed_target: transformed.append(transformed_target)
            random.Random(SEED + n*163).shuffle(source)
            random.Random(SEED + n*719).shuffle(transformed)
            i_source=source.index(source_target) if source_target else None
            i_trans=transformed.index(transformed_target) if transformed_target else None
            direction=("source_to_transformed" if group=="omitted_allergy"
                       else "transformed_to_source")
            row={
                "id":f"CD-LOCK-{n:03d}",
                "source_units":source,"transformed_units":transformed,
                "source_text":" ".join(source),"transformed_text":" ".join(transformed),
                "source_target_index":i_source,"transformed_target_index":i_trans,
                "target_pair_exists":i_source is not None and i_trans is not None,
                "gold_direction":direction,
                "gold_source_candidate_index":i_source,
                "gold_transformed_candidate_index":i_trans,
                "nli_relation_oracle":nli_label,
                "integrity_error":error,
                "meaning_preserving_control":not error,
                "drift_category":group,
                "scenario_family":"separately_constructed_v2_"+group,
                "template_family":"locked_v2_"+group,
                "provenance":"synthetic",
                "annotation_rationale":"Known transformation in generator, not independently reviewed or clinically adjudicated.",
                "adjudication_status":"pending",
                "independent_check_label":None,
                "construction_version":"2026-10-25-v2",
            }
            out.append(row)
    assert len(out)==EXPECTED
    assert sum(r["integrity_error"] for r in out)==200
    assert sum(r["meaning_preserving_control"] for r in out)==80
    assert {r["adjudication_status"] for r in out}=={"pending"}
    assert len({r["source_target_index"] for r in out if r["source_target_index"] is not None})>1
    assert len({r["transformed_target_index"] for r in out if r["transformed_target_index"] is not None})>1
    assert len({(r["source_text"],r["transformed_text"]) for r in out})==len(out)
    return out

def write_jsonl(path, rows):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="\n") as file:
        for row in rows:
            file.write(json.dumps(row,sort_keys=True,ensure_ascii=False)+"\n")
    return hashlib.sha256(path.read_bytes()).hexdigest()

if __name__=="__main__":
    from argparse import ArgumentParser
    p=ArgumentParser();p.add_argument("--output",required=True)
    args=p.parse_args()
    rows=construction(); path=Path(args.output)
    digest=write_jsonl(path,rows)
    print(json.dumps({"cases":len(rows),"error_count":200,"control_count":80,
                      "sha256":digest,"categories":dict(Counter(r["drift_category"] for r in rows)),
                      "adjudication":"pending; not independently reviewed","source":"code-generated new benchmark"},
                      indent=2))
