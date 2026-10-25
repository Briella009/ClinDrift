"""Recompute and audit the October 2026 ClinDrift pilot from immutable raw files.

Run: python evaluation/masters_nli/archive_and_audit.py
No transformer dependency, no benchmark modifications, no rerunning inference.
"""
from __future__ import annotations
import collections
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]/"evaluation"/"experiments"/"2026-10-25"
PILOT = ROOT/"pilot_v1"
RAW = PILOT/"raw"
ZIP_SHA = "7d62af4e119f2b8e70ba2965ea68fdef40f44e13a055c042cfa859dabd28068e"
RUN_ID = 40168975981
SOURCE_SHA = "2d412af5d63aec9839fbbebb31c540149e203b56"

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True)+"\n", encoding="utf-8")

def confusion(rows, flags):
    assert len(rows)==len(flags)
    tp=sum(bool(r["integrity_error"]) and bool(f) for r,f in zip(rows,flags))
    fn=sum(bool(r["integrity_error"]) and not bool(f) for r,f in zip(rows,flags))
    fp=sum(not bool(r["integrity_error"]) and bool(f) for r,f in zip(rows,flags))
    tn=sum(not bool(r["integrity_error"]) and not bool(f) for r,f in zip(rows,flags))
    return {"TP":tp,"FN":fn,"FP":fp,"TN":tn,
      "recall":tp/(tp+fn),"precision":tp/(tp+fp),
      "false_positive_rate":fp/(fp+tn),
      "f1":2*tp/(2*tp+fp+fn),
      "accuracy":(tp+tn)/(tp+fn+fp+tn)}

def main():
    assert sha256(PILOT/"original_artifact.zip")==ZIP_SHA, "Original archive altered"
    cases=read_jsonl(RAW/"synthetic_heldout_pilot_280.jsonl")
    dev=read_jsonl(RAW/"development_140_derived_nli.jsonl")
    paired=read_jsonl(RAW/"pilot_case_level_paired_results_280.jsonl")
    nli=read_jsonl(RAW/"pilot_oracle_predictions_280.jsonl")
    pair_records=read_jsonl(RAW/"pilot_pairing_predictions_280.jsonl")
    summary=read_json(RAW/"pilot_result_summary.json")
    protocol=read_json(RAW/"selection_protocol_executed.json")
    calibration=read_json(RAW/"development_calibration.json")
    assert len(cases)==len(paired)==len(nli)==len(pair_records)==280
    assert sha256(RAW/"synthetic_heldout_pilot_280.jsonl")==summary["benchmark_sha256"]
    assert (RAW/"source_commit.txt").read_text().strip()==SOURCE_SHA
    assert all(r["adjudication_status"]=="pending" for r in cases)
    assert all(c["id"]==p["id"]==n["id"] for c,p,n in zip(cases,paired,nli))
    baseline=[p["baseline_flag"] for p in paired]
    hybrid=[p["oracle_hybrid_flag"] for p in paired]
    assert hybrid==[p["end_to_end_top1_hybrid_flag"] for p in paired]
    current={"rules":confusion(cases,baseline),"hybrid":confusion(cases,hybrid)}
    for key,label in [("rules","pilot_rules"),("hybrid","pilot_hybrid_oracle")]:
        for k,v in current[key].items():
            assert abs(v-summary[label][k]) < 1e-9,(key,k,v,summary[label][k])
    sids=set(protocol["selection_ids"]); cids=set(protocol["calibration_ids"])
    assert not sids&cids
    sel_families={r["template_family"] for r in dev if r["id"] in sids}
    cal_families={r["template_family"] for r in dev if r["id"] in cids}
    gold_at_zero=sum(1 for r in cases if r["gold_query_index"]==0 and r["gold_candidate_indices"]==[0])
    confusion_nli=collections.Counter((r["label"],p["label"]) for r,p in zip(cases,nli))
    category_counts={}
    for group in sorted({r["drift_category"] for r in cases}):
        ids=[i for i,r in enumerate(cases) if r["drift_category"]==group]
        category_counts[group]={"n":len(ids),"errors":sum(cases[i]["integrity_error"] for i in ids),
         "rules_flags":sum(baseline[i] for i in ids),
         "hybrid_flags":sum(hybrid[i] for i in ids),
         "nli_relation_accuracy":sum(cases[i]["label"]==nli[i]["label"] for i in ids)/len(ids)}
    # This estimates nonconcordant added findings, not clinically confirmed errors.
    gained=[i for i in range(len(cases)) if cases[i]["integrity_error"] and hybrid[i] and not baseline[i]]
    wrong_rel=sum(nli[i]["label"]!=cases[i]["label"] for i in gained)
    audit={
       "historical_run_id":RUN_ID,"historical_source_sha":SOURCE_SHA,
       "zip_sha256":ZIP_SHA,"cases":len(cases),"results_recomputed":current,
       "case_selection_calibration_disjoint":True,
       "shared_selection_calibration_template_family_count":len(sel_families&cal_families),
       "gold_query_and_candidate_always_at_index_zero":gold_at_zero,
       "nli_relation_confusion":{a+" -> "+b:c for (a,b),c in confusion_nli.items()},
       "newly_flagged_error_cases":len(gained),
       "newly_flagged_error_cases_with_wrong_nli_relation":wrong_rel,
       "by_category":category_counts,
       "reported_pairing_recall_at_1":summary["pairing_recall_at_1"],
       "calibration_temperature":calibration["temperature"],
       "selected_threshold":calibration["selected_threshold"],
       "corrections":[
          "Target-specified pairing used a gold direction and selected only query index 0; not a genuine all-sentence end-to-end test.",
          "All 280 gold target pairs were at (0,0); recall@1=100% is artificially easy and recall@3 covers all three sentences.",
          "Selection and calibration split had disjoint cases but shared template families.",
          "No independent adjudication; benchmark rows remain pending and were not final-frozen.",
          "Positive-case flag recall does not require correct clinical mechanism or gold NLI relation.",
          "The original RSS number is a one-time memory sample, not a peak.",
          "Previous bootstrap interval measured difference in overall flag rate, not difference in recall.",
          "No clinician evaluation, clinical generalization, externally judged correctness, or production integration was tested."
       ],
       "status":"audited exploratory synthetic pilot, NOT a final clinically validated result"
    }
    write(PILOT/"AUDIT.json",audit)
    (PILOT/"SHA256SUMS.txt").write_text("".join(
        f"{sha256(f)}  {f.relative_to(PILOT)}\n"
        for f in sorted(PILOT.rglob("*")) if f.is_file() and f.name!="SHA256SUMS.txt"
    ),encoding="utf-8")
    print(json.dumps({"status":"audit_passed","old_counts":current,
          "shared_template_families":len(sel_families&cal_families),
          "gold_at_index_zero":gold_at_zero,
          "additional_flags_wrong_relation":wrong_rel},indent=2))

if __name__=="__main__":main()
