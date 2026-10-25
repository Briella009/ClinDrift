"""Strict, no-model verification of the committed locked-v2 results.

Run on a checkout of the research branch:
python evaluation/masters_nli/verify_locked_v2.py
"""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/"evaluation"/"experiments"/"2026-10-25"/"locked_v2"
PROTO=ROOT/"evaluation"/"masters_nli"/"locked_v2_protocol.json"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]

def confusion(rows,flags):
    tp=sum(r["integrity_error"] and f for r,f in zip(rows,flags))
    fn=sum(r["integrity_error"] and not f for r,f in zip(rows,flags))
    fp=sum(not r["integrity_error"] and f for r,f in zip(rows,flags))
    tn=sum(not r["integrity_error"] and not f for r,f in zip(rows,flags))
    return {"TP":tp,"FN":fn,"FP":fp,"TN":tn}

def main():
    dataset_path=RUN/"locked_synthetic_280.jsonl"
    result=json.loads((RUN/"LOCKED_TECHNICAL_RESULTS.json").read_text())
    pre=json.loads((RUN/"PRE_INFERENCE_FREEZE.json").read_text())
    post=json.loads((RUN/"POST_RUN_INTEGRITY.json").read_text())
    cases=jsonl(dataset_path)
    preds=jsonl(RUN/"FULL_DOCUMENT_RAW_PREDICTIONS_280.jsonl")
    pairs=jsonl(RUN/"EVIDENCE_PAIR_RETRIEVAL_280.jsonl")
    oracle=jsonl(RUN/"ORACLE_TARGET_PREDICTIONS.jsonl")
    assert len(cases)==len(preds)==len(pairs)==280
    assert len(oracle)==220
    assert sum(r["integrity_error"] for r in cases)==200
    assert sum(r["meaning_preserving_control"] for r in cases)==80
    assert all(r["adjudication_status"]=="pending" for r in cases)
    assert all(a["id"]==b["id"]==c["id"] for a,b,c in zip(cases,preds,pairs))
    assert digest(dataset_path)==result["dataset_sha256"]==pre["dataset_sha256"]==post["end_dataset_sha256"]
    assert digest(PROTO)==pre["protocol_sha256"]==post["end_protocol_sha256"]
    assert post["identical_after_inference"] is True
    assert pre["model_checkpoint"]=="6f5cf0a2b59cabb106aca4c287eed12e357e90eb"
    baseline=[r["baseline_flag"] for r in preds]
    hybrid=[r["hybrid_flag"] for r in preds]
    counts={
      "rules":confusion(cases,baseline),
      "hybrid":confusion(cases,hybrid)}
    for key,src in [("rules","baseline_case_metrics"),("hybrid","hybrid_case_metrics")]:
        assert counts[key]=={k:result[src][k] for k in ("TP","FN","FP","TN")}
    assert sum(r["review_required"] for r in preds)==result["review_required_n"]
    assert sum(r["any_gold_aligned_ai_contradiction"] for r in preds)==result["gold_aligned_ai_contradiction_case_count"]
    lookup={r["id"]:r for r in cases}
    actual_correct=sum(x["gold_label"]==x["label"] for x in oracle)
    assert actual_correct==180
    assert sum(a["retrieval"]["top1"]["hits"] for a in pairs)==440
    assert sum(a["retrieval"]["top3"]["hits"] for a in pairs)==440
    assert result["number_of_evaluable_directional_gold_pairs"]==440
    assert abs(result["review_burden"]-240/280)<1e-10
    assert len({r["scenario_family"] for r in cases})==14
    bad_control=[r["category"] for r in preds if r["hybrid_flag"] and not r["ground_truth_error_author_constructed"]]
    assert Counter(bad_control)==Counter({"afebrile_paraphrase_control":20})
    for row in preds:
        for p in row["candidate_predictions"]:
            score=p["raw_scores"];scaled=p["scaled_scores"]
            assert abs(sum(score.values())-1)<1e-5
            assert abs(sum(scaled.values())-1)<1e-5
    verified=[]
    for line in (RUN/"SHA256SUMS.txt").read_text().splitlines():
        digest_expected,relative=line.split("  ",1)
        if relative=="SHA256SUMS.txt":continue
        path=RUN/relative
        assert path.exists(),path
        assert digest(path)==digest_expected,(relative,"hash changed")
        verified.append(relative)
    print(json.dumps({"status":"VERIFIED","cases":280,"oracle_correct":actual_correct,
      "baseline":counts["rules"],"hybrid":counts["hybrid"],
      "false_control_families":dict(Counter(bad_control)),
      "audited_files":len(verified),"dataset_sha256":digest(dataset_path),
      "boundary":"No independent label adjudication; technical study only"},indent=2))
if __name__=="__main__":
    main()
