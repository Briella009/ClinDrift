"""Run evidence-preserving ClinDrift technical research experiments.

Not clinical validation. Candidate selection uses the historical 140-case data
only; 280 separately constructed synthetic pilot cases have labels PENDING
independent review. A pilot score cannot be called the final frozen study.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import os
import platform
import statistics
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from evaluation.masters_nli.experiment_data import (
    development_cases, synthetic_pilot, verify_disjoint, write_jsonl, SEED,
)
from evaluation.masters_nli.freeze_benchmark import freeze
from src.extractor import extract_facts
from src.drift_engine import compare_facts
from src.evidence_pairing import bidirectional_pairing, pairing_recall_at_k
from src.decision_fusion import reconcile

MODELS = (
    ("general_small", "cross-encoder/nli-deberta-v3-small"),
    ("general_factcheck_base", "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"),
    ("biomedical_pubmedbert", "pritamdeka/PubMedBERT-MNLI-MedNLI"),
    ("general_minilm", "cross-encoder/nli-MiniLM2-L6-H768"),
)
LABELS = ("contradiction","entailment","neutral")
EXPLORATORY = (
    "This is a synthetic, author-generated, not independently adjudicated "
    "pilot. It is not the final master's held-out performance estimate, "
    "clinical validation, a medical-device claim, or a patient-safety outcome."
)

def now():
    return datetime.now(timezone.utc).isoformat()

def write_json(path: Path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True, default=str)+"\n", encoding="utf-8")

def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]

def safe_ratio(a,b):
    return a/b if b else None

def binary_counts(rows, flags):
    assert len(rows)==len(flags)
    tn=tp=fn=fp=0
    for r, flag in zip(rows,flags):
        if r["integrity_error"] and flag:tp+=1
        elif r["integrity_error"] and not flag:fn+=1
        elif not r["integrity_error"] and flag:fp+=1
        else:tn+=1
    prec=safe_ratio(tp,tp+fp)
    rec=safe_ratio(tp,tp+fn)
    return {"n":len(rows),"TP":tp,"FP":fp,"TN":tn,"FN":fn,
        "precision":prec,"recall":rec,
        "specificity":safe_ratio(tn,tn+fp),
        "false_positive_rate":safe_ratio(fp,fp+tn),
        "accuracy":(tp+tn)/len(rows),
        "f1":2*prec*rec/(prec+rec) if prec is not None and rec is not None and prec+rec else None}

def baseline_flags(rows):
    results=[]
    for row in rows:
        found=compare_facts(extract_facts(row["source_text"]), extract_facts(row["transformed_text"]))
        results.append(bool(found))
    return results

def save_baseline(output):
    out=Path(output)
    dev=development_cases()
    hold=synthetic_pilot()
    disjoint=verify_disjoint(dev,hold)
    dh=write_jsonl(out/"development_140_derived_nli.jsonl",dev)
    hh=write_jsonl(out/"synthetic_heldout_pilot_280.jsonl",hold)
    manifest=freeze(out/"synthetic_heldout_pilot_280.jsonl",mode="nli",final=False,
                    development_path=out/"development_140_derived_nli.jsonl")
    # Never change pending annotation to agreed or adjudicated on the basis of a generator.
    assert not manifest["final_freeze"] and all(r["adjudication_status"]=="pending" for r in hold)
    write_json(out/"pilot_manifest_NOT_FINAL.json",manifest)
    devflags=baseline_flags(dev); heldflags=baseline_flags(hold)
    write_jsonl(out/"baseline_case_predictions_280.jsonl",
        [{ "id":r["id"],"drift_category":r["drift_category"],
           "integrity_error":r["integrity_error"],"baseline_flag":flag
         } for r,flag in zip(hold,heldflags)])
    summary={
        "timestamp_utc":now(),"dataset_development_sha256":dh,
        "dataset_new_pilot_sha256":hh,"new_pilot_status":"pending human annotation review",
        "predeclared_seed":SEED,
        "leakage_audit":disjoint,
        "development_nli_relation_counts":dict(Counter(x["label"] for x in dev)),
        "pilot_nli_relation_counts":dict(Counter(x["label"] for x in hold)),
        "pilot_category_counts":dict(Counter(x["drift_category"] for x in hold)),
        "development_rules":binary_counts(dev,devflags),
        "new_pilot_rules":binary_counts(hold,heldflags),
        "reporting_boundary":EXPLORATORY,
        "runtime":{"python":platform.python_version(),"platform":platform.platform(),
                   "cpu_count":os.cpu_count()},
    }
    write_json(out/"pre_model_baseline_summary.json",summary)
    print("BASELINE_RESULTS "+json.dumps(summary))
    return dev,hold

def ece(conf,correct,n_bins=10):
    if not conf: return None
    n=len(conf); total=0.
    for k in range(n_bins):
        ix=[i for i,p in enumerate(conf)
            if (k/n_bins <=p < (k+1)/n_bins) or (k==n_bins-1 and p==1)]
        if ix:
            total += len(ix)/n*abs(sum(conf[i] for i in ix)/len(ix) -
                                    sum(correct[i] for i in ix)/len(ix))
    return total

def metric_rows(rows, preds, threshold=None):
    assert len(rows)==len(preds)
    if not rows:return {}
    threshold=0.80 if threshold is None else threshold
    gold=[r["label"] for r in rows]
    predicted=[p["label"] for p in preds]
    auto=[p["label"]=="contradiction" and p["scores"]["contradiction"]>=threshold for p in preds]
    ctrls=[i for i,r in enumerate(rows) if r["meaning_preserving_control"]]
    sem=[i for i,r in enumerate(rows) if r["drift_category"] in
       ("semantic_contradiction","consciousness_contradiction","symptom_course_contradiction")]
    critical=[i for i,r in enumerate(rows) if r["severity"]=="Critical" and r["integrity_error"]]
    flagged_indices=[i for i,x in enumerate(auto) if x]
    accuracy=sum(a==b for a,b in zip(gold,predicted))/len(gold)
    class_metrics={}
    for cls in LABELS:
        tp=sum(a==cls and b==cls for a,b in zip(gold,predicted))
        fp=sum(a!=cls and b==cls for a,b in zip(gold,predicted))
        fn=sum(a==cls and b!=cls for a,b in zip(gold,predicted))
        p=safe_ratio(tp,tp+fp) or 0.
        r=safe_ratio(tp,tp+fn) or 0.
        class_metrics[cls]={"precision":p,"recall":r,"f1":2*p*r/(p+r) if p+r else 0.,
                            "support":sum(a==cls for a in gold)}
    conf=[max(p["scores"].values()) for p in preds]
    ok=[a==b for a,b in zip(gold,predicted)]
    nll=-sum(math.log(max(p["scores"][r["label"]],1e-12)) for r,p in zip(rows,preds))/len(rows)
    brier=sum(sum((p["scores"][cls]-(1. if cls==r["label"] else 0.))**2 for cls in LABELS)
              for r,p in zip(rows,preds))/len(rows)
    lat=[p.get("latency_ms",0.) for p in preds]
    return {
        "n":len(rows), "accuracy":accuracy,
        "macro_f1":statistics.mean(x["f1"] for x in class_metrics.values()),
        "nli_per_class":class_metrics,
        "semantic_challenge_auto_recall":safe_ratio(sum(auto[i] for i in sem),len(sem)),
        "semantic_challenge_n":len(sem),
        "flagged_finding_precision":safe_ratio(sum(rows[i]["integrity_error"] for i in flagged_indices),
                                             len(flagged_indices)),
        "flagged_n":len(flagged_indices),
        "false_positive_rate_controls":safe_ratio(sum(auto[i] for i in ctrls),len(ctrls)),
        "controls_n":len(ctrls),
        "critical_category_auto_recall":safe_ratio(sum(auto[i] for i in critical),len(critical)),
        "critical_category_review_routing_recall":safe_ratio(sum(
            auto[i] or preds[i]["label"]=="neutral" for i in critical),len(critical)),
        "critical_n":len(critical),
        "uncertain_neutral_review_rate":sum(p["label"]=="neutral" for p in preds)/len(preds),
        "ece_top_label":ece(conf,ok),"multiclass_brier":brier,"negative_log_likelihood":nll,
        "p50_inference_ms":statistics.median(lat),
        "p95_inference_ms":sorted(lat)[int(.95*(len(lat)-1))],
        "decision_threshold":threshold,
        "inference_timing_boundary":"forward pass incl. CPU softmax, excludes tokenization, loading and full UI",
    }

def selection_score(m):
    # Predeclared development-only utility, not a validated clinical cost function.
    get=lambda k: float(m[k] or 0.)
    return round(0.35*get("semantic_challenge_auto_recall")+
                 0.25*get("flagged_finding_precision")+
                 0.20*get("critical_category_auto_recall")+
                 0.20*(1-get("false_positive_rate_controls")),6)

class CPUModel:
    def __init__(self,name, revision):
        import torch
        from transformers import AutoTokenizer,AutoModelForSequenceClassification
        torch.set_num_threads(2)
        self.torch=torch; self.name=name; self.revision=revision
        self.tokenizer=AutoTokenizer.from_pretrained(name,revision=revision,trust_remote_code=False)
        self.model=AutoModelForSequenceClassification.from_pretrained(
            name,revision=revision,trust_remote_code=False)
        self.model.eval()
        if int(self.model.config.num_labels)!=3:
            raise ValueError(f"Expected three NLI labels: {self.model.config.id2label}")
        raw=[str(self.model.config.id2label.get(i,"")).strip().lower() for i in range(3)]
        if set(raw)!=set(LABELS):
            raise ValueError(f"UNKNOWN MODEL LABEL MAP {name}: {raw}; explicit validation required; no guessing")
        self.labels=raw
        self.param_count=sum(p.numel() for p in self.model.parameters())

    def predict(self, row: dict):
        enc=self.tokenizer(row["premise"],row["hypothesis"],return_tensors="pt",
                           max_length=512,truncation=True)
        start=time.perf_counter()
        with self.torch.inference_mode():
            probs=self.torch.softmax(self.model(**enc).logits[0],dim=-1).cpu().tolist()
        ms=(time.perf_counter()-start)*1000.
        scores={label:float(p) for label,p in zip(self.labels,probs)}
        return {"id":row["id"],"label":max(scores,key=scores.get),
                "scores":scores,"latency_ms":ms}

def temperature_scale(scores, t):
    import numpy as np
    a=np.log(np.clip(np.asarray([scores[x] for x in LABELS]),1e-9,1.))/t
    a=a-a.max(); p=np.exp(a);p=p/p.sum()
    return {k:float(v) for k,v in zip(LABELS,p)}

def fit_temperature(rows, preds):
    from scipy.optimize import minimize_scalar
    def nll(t):
        return -sum(math.log(max(temperature_scale(p["scores"],t)[r["label"]],1e-9))
                    for r,p in zip(rows,preds))/len(rows)
    result=minimize_scalar(nll,bounds=(0.5,5.0),method="bounded",
                           options={"xatol":1e-3})
    return float(result.x),float(result.fun)

def calibrate_preds(preds,t):
    res=[]
    for p in preds:
        s=temperature_scale(p["scores"],t)
        res.append({**p,"uncalibrated_scores":p["scores"],
                    "scores":s,"label":max(s,key=s.get)})
    return res

def split_dev(rows):
    counts=Counter(); choice=[]; cal=[]
    for r in rows:
        within=counts[r["drift_category"]]
        counts[r["drift_category"]]+=1
        (cal if within % 5 == 0 else choice).append(r)
    return choice,cal

def choose_threshold(rows, preds):
    # Selection uses calibration subset only, never pilot labels.
    candidates=[]
    for threshold in [0.5,0.6,0.7,0.8,0.9]:
        m=metric_rows(rows,preds,threshold)
        score=selection_score(m)
        candidates.append({"threshold":threshold,"score":score,
                          "metrics":m})
    candidates.sort(key=lambda x:(x["score"],-x["threshold"]),reverse=True)
    return candidates[0]["threshold"],candidates

def paired_comparison(rows, a, b):
    from scipy.stats import binomtest
    import numpy as np
    n01=n10=0
    for r,x,y in zip(rows,a,b):
        ac=(bool(x)==bool(r["integrity_error"]))
        bc=(bool(y)==bool(r["integrity_error"]))
        if not ac and bc:n01+=1
        if ac and not bc:n10+=1
    p=binomtest(n01,n01+n10,0.5).pvalue if n01+n10 else 1.
    rng=np.random.default_rng(SEED)
    diffs=[];values=np.array([int(y)-int(x) for x,y in zip(a,b)])
    for _ in range(1000):
        ids=rng.integers(0,len(values),size=len(values))
        diffs.append(float(values[ids].mean()))
    return {
        "baseline_incorrect_hybrid_correct":n01,"baseline_correct_hybrid_incorrect":n10,
        "mcnemar_exact_two_sided_p":p,
        "mean_flag_rate_difference":float(values.mean()),
        "paired_bootstrap_flag_rate_difference_95pct_interval":list(np.quantile(diffs,[0.025,0.975])),
        "interpretation":"Exploratory pilot only; sample labels pending review, not a confirmatory hypothesis test",
    }

def model_stage(out):
    import psutil
    from huggingface_hub import HfApi
    dev=read_jsonl(out/"development_140_derived_nli.jsonl")
    pilot=read_jsonl(out/"synthetic_heldout_pilot_280.jsonl")
    selection,calibration=split_dev(dev)
    sids={r["id"] for r in selection};cids={r["id"] for r in calibration}
    assert len(sids&cids)==0 and len(sids|cids)==len(dev)
    predeclared={"selection_ids":sorted(sids),"calibration_ids":sorted(cids),
      "candidate_names":dict(MODELS),"selection_score_weights":
      {"semantic_challenge_recall":0.35,"flagged_precision":0.25,
       "critical_auto_recall":0.2,"1_minus_control_false_positive":0.2},
      "threshold_grid":[0.5,0.6,0.7,0.8,0.9],
      "evaluation_locks":"No pilot outcomes used to rank candidates or fit temperature/threshold",
      "critical_severity":"synthetic experiment severity heuristic, not expert-validated",
      "test_set_status":"pilot; labels pending human review",
      "created_at_utc":now()}
    write_json(out/"selection_protocol_executed.json",predeclared)
    api=HfApi()
    candidates=[]
    for short,name in MODELS:
        result={"id":short,"name":name,"started_at_utc":now(),"status":"running"}
        try:
            rev=api.model_info(name).sha
            result["revision_sha"]=rev
            started=time.perf_counter()
            model=CPUModel(name,rev)
            result["load_seconds"]=time.perf_counter()-started
            result["parameter_count"]=model.param_count
            result["label_mapping"]=model.labels
            raw=[model.predict(r) for r in dev]
            write_jsonl(out/f"development_raw_predictions_{short}.jsonl",raw)
            pred_by_id={p["id"]:p for p in raw}
            sel_pred=[pred_by_id[r["id"]] for r in selection]
            result["selection_metrics"]=metric_rows(selection,sel_pred,0.8)
            result["selection_score"]=selection_score(result["selection_metrics"])
            result["dev_full_diagnostic"]=metric_rows(dev,raw,0.8)
            result["load_and_infer_completed_at_utc"]=now()
            result["status"]="completed"
        except Exception as ex:
            result["status"]="failed";result["error_type"]=type(ex).__name__
            result["error"]=str(ex)[:1500]
            result["traceback"]=traceback.format_exc()[-3000:]
        candidates.append(result)
        write_json(out/"candidate_status.json",{"candidates":candidates,
            "completed_at":now(),"reporting_boundary":EXPLORATORY})
        print("MODEL_RESULT "+json.dumps({k:v for k,v in result.items()
              if k in {"id","name","status","selection_score","error"}}),flush=True)
        try:
            del model
        except UnboundLocalError: pass
        gc.collect()
    passed=[x for x in candidates if x["status"]=="completed"]
    if not passed:
        write_json(out/"experiment_final_status.json",{"status":"blocked_all_candidates_failed",
          "candidates":candidates,"reporting_boundary":EXPLORATORY})
        raise RuntimeError("No candidate loaded and produced validated predictions")
    passed.sort(key=lambda x:(x["selection_score"],
                              -x["selection_metrics"]["false_positive_rate_controls"],
                              -x["selection_metrics"]["p50_inference_ms"]),reverse=True)
    chosen=passed[0]
    selection_complete=len(passed)==len(MODELS)
    write_json(out/"provisional_candidate_selection.json",{
        "chosen_model":chosen["name"],"chosen_revision_sha":chosen["revision_sha"],
        "selection_complete_four_candidates":selection_complete,
        "success_count":len(passed),"registered_count":len(MODELS),
        "ranking":[{"id":c["id"],"score":c["selection_score"]} for c in passed],
        "status":"provisional: not a complete four-model comparison" if not selection_complete
                else "development-only candidate ranking; pilot not used",
        "reporting_boundary":EXPLORATORY,
    })
    model=CPUModel(chosen["name"],chosen["revision_sha"])
    raw_dev=read_jsonl(out/f"development_raw_predictions_{chosen['id']}.jsonl")
    by_id={p["id"]:p for p in raw_dev}
    cal_raw=[by_id[r["id"]] for r in calibration]
    temp,fit_loss=fit_temperature(calibration,cal_raw)
    cal_preds=calibrate_preds(cal_raw,temp)
    threshold,search=choose_threshold(calibration,cal_preds)
    write_json(out/"development_calibration.json",{
       "model":chosen["name"],"revision_sha":chosen["revision_sha"],
       "calibration_sample_count":len(calibration),
       "fit_on_same_rows_used_for_threshold":"Yes; thresholds exploratory and susceptible to optimism",
       "temperature":temp,"fit_nll":fit_loss,
       "before_calibration":metric_rows(calibration,cal_raw,0.80),
       "after_calibration":metric_rows(calibration,cal_preds,threshold),
       "threshold_grid":search,"selected_threshold":threshold,
       "reporting_boundary":EXPLORATORY,
    })
    held_oracle=[]
    held_auto=[]
    pair_records=[]
    for index,r in enumerate(pilot):
        oracle=model.predict(r)
        held_oracle.append(oracle)
        pairing={}
        for k in (1,3):
            options=bidirectional_pairing(r["source_text"],r["transformed_text"],top_k=k)
            candidates=options[r["direction"]]
            q0=[c for c in candidates if c.query_index==0]
            pair_metric=pairing_recall_at_k(q0,{(0,0)})
            pairing[str(k)]={"gold_pair_recalled":pair_metric==1.0,
                             "recall":pair_metric,
                             "candidate_indices":[c.candidate_index for c in q0]}
            if k==1:
                if not q0:raise RuntimeError(f"Pairing yielded no candidate for {r['id']}")
                first=q0[0]
                auto_input={"id":r["id"],"premise":first.candidate_text,
                            "hypothesis":first.query_text}
                if r["direction"]=="transformed_to_source":
                    auto_input={"id":r["id"],"premise":first.candidate_text,
                                "hypothesis":first.query_text}
                # In both directions, the candidate text is the NLI premise.
                automatic=model.predict(auto_input)
                held_auto.append(automatic)
        pair_records.append({"id":r["id"],"direction":r["direction"],
             "drift_category":r["drift_category"],"top1":pairing["1"],
             "top3":pairing["3"]})
        if (index+1)%25==0:
            print(f"PILOT_PROGRESS completed={index+1}/{len(pilot)}",flush=True)
    write_jsonl(out/"pilot_oracle_predictions_280.jsonl",held_oracle)
    write_jsonl(out/"pilot_automatic_top1_predictions_280.jsonl",held_auto)
    write_jsonl(out/"pilot_pairing_predictions_280.jsonl",pair_records)
    or_cal=calibrate_preds(held_oracle,temp)
    au_cal=calibrate_preds(held_auto,temp)
    base=baseline_flags(pilot)
    def case_decisions(preds):
        flags=[];reviews=[]
        for flag,p in zip(base,preds):
            confidence=p["scores"][p["label"]]
            decision=reconcile(deterministic_positive=flag,deterministic_equivalent=False,
              nli_label=p["label"],nli_confidence=confidence,
              contradiction_threshold=threshold)
            flags.append(decision.final_status=="finding")
            reviews.append(decision.requires_review)
        return flags,reviews
    oracle_flags,oracle_reviews=case_decisions(or_cal)
    auto_flags,auto_reviews=case_decisions(au_cal)
    write_jsonl(out/"pilot_case_level_paired_results_280.jsonl",[
       {"id":r["id"],"category":r["drift_category"],"label_pending_review":r["label"],
        "integrity_error_pending_review":r["integrity_error"],
        "baseline_flag":bf,"oracle_hybrid_flag":of,"end_to_end_top1_hybrid_flag":af,
        "oracle_review_required":ov,"top1_review_required":av,
        "oracle_raw_prediction":p0,"top1_raw_prediction":p1}
       for r,bf,of,af,ov,av,p0,p1 in
       zip(pilot,base,oracle_flags,auto_flags,oracle_reviews,auto_reviews,held_oracle,held_auto)
    ])
    result={
      "status":"exploratory_280_case_synthetic_pilot_not_final",
      "four_model_comparison_completed":selection_complete,
      "candidate_selected_for_exploratory_pilot":chosen["name"],
      "model_revision":chosen["revision_sha"],
      "temperature_dev_only":temp,
      "contradiction_decision_threshold_dev_only":threshold,
      "n_pilot":len(pilot),
      "benchmark_sha256":hashlib.sha256((out/"synthetic_heldout_pilot_280.jsonl").read_bytes()).hexdigest(),
      "pilot_nli_oracle":metric_rows(pilot,or_cal,threshold),
      "pilot_nli_top1_automatic_pairing":metric_rows(pilot,au_cal,threshold),
      "pilot_rules":binary_counts(pilot,base),
      "pilot_hybrid_oracle":binary_counts(pilot,oracle_flags),
      "pilot_hybrid_top1":binary_counts(pilot,auto_flags),
      "oracle_review_burden":sum(oracle_reviews)/len(pilot),
      "automatic_top1_review_burden":sum(auto_reviews)/len(pilot),
      "pairing_recall_at_1":sum(x["top1"]["recall"] for x in pair_records)/len(pair_records),
      "pairing_recall_at_3":sum(x["top3"]["recall"] for x in pair_records)/len(pair_records),
      "paired_test_rules_vs_oracle":paired_comparison(pilot,base,oracle_flags),
      "paired_test_rules_vs_automatic_top1":paired_comparison(pilot,base,auto_flags),
      "peak_memory_rss_bytes":__import__("psutil").Process().memory_info().rss,
      "run_utc":now(),
      "limitations":["No independent or clinical adjudication of labels",
        "Not a clinically validated severity rubric","Separate CLI hybrid evaluation, not proof of Streamlit integration",
        "No prospective patient-derived data","Model selection from limited known synthetic cases",
        "Temperature and threshold fitted on the same small calibration subset",
        "Automatic pairing top-1 lexical baseline only"],
      "reporting_boundary":EXPLORATORY,
    }
    write_json(out/"pilot_result_summary.json",result)
    print("EXPLORATORY_PILOT_RESULT "+json.dumps({
        "selected":result["candidate_selected_for_exploratory_pilot"],
        "baseline":result["pilot_rules"],
        "oracle":result["pilot_hybrid_oracle"],
        "top1":result["pilot_hybrid_top1"],
        "pairing_recall_at_1":result["pairing_recall_at_1"]}),flush=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--stage",choices=("baseline","models"),required=True)
    p.add_argument("--output",type=Path,default=Path("experiment_outputs"))
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    if a.stage=="baseline":save_baseline(a.output)
    else:model_stage(a.output)

if __name__=="__main__":main()
