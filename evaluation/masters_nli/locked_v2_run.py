"""Locked multi-sentence bidirectional synthetic technical evaluation.

No post-result hyperparameter selection and no patient-derived data.
A separate SHA-256-locked synthetic dataset is generated before loading the
previously selected NLI checkpoint. No gold target position or direction is
supplied to retrieval. Dataset labels are researcher-constructed and pending
independent checking, so findings are not clinical validation.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
import os
import platform
import statistics
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from evaluation.masters_nli.locked_v2_data import construction,write_jsonl
from src.extractor import extract_facts
from src.drift_engine import compare_facts
from src.evidence_pairing import bidirectional_pairing

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,indent=2,sort_keys=True,ensure_ascii=False,default=str)+"\n",encoding="utf-8")
def now():return datetime.now(timezone.utc).isoformat()

def metrics(rows, flags):
    assert len(rows)==len(flags)
    tp=sum(r["integrity_error"] and bool(x) for r,x in zip(rows,flags))
    fn=sum(r["integrity_error"] and not bool(x) for r,x in zip(rows,flags))
    fp=sum((not r["integrity_error"]) and bool(x) for r,x in zip(rows,flags))
    tn=sum((not r["integrity_error"]) and not bool(x) for r,x in zip(rows,flags))
    return {"n":len(rows),"TP":tp,"FN":fn,"FP":fp,"TN":tn,
      "recall":tp/(tp+fn) if tp+fn else None,
      "precision":tp/(tp+fp) if tp+fp else None,
      "false_positive_rate":fp/(fp+tn) if fp+tn else None,
      "accuracy":(tp+tn)/len(rows) if rows else None,
      "f1":2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None}

def prob_temp(scores,temp):
    labels=("entailment","neutral","contradiction")
    a=[math.log(max(min(float(scores[x]),1.),1e-10))/temp for x in labels]
    mx=max(a);v=[math.exp(x-mx) for x in a];tot=sum(v)
    return {x:y/tot for x,y in zip(labels,v)}

def compute_ece(confs,accurate,bins=10):
    if not confs:return None
    total=0.
    for j in range(bins):
        idx=[i for i,x in enumerate(confs) if (j/bins<=x<(j+1)/bins) or (j==bins-1 and x==1)]
        if idx:
            total+=len(idx)/len(confs)*abs(
                sum(confs[i] for i in idx)/len(idx)-
                sum(accurate[i] for i in idx)/len(idx))
    return total

def classify_oracle(rows,preds,temperature):
    if not rows:return None
    assert len(rows)==len(preds)
    correct=[];confs=[];brier=0.;nll=0.
    for row,pred in zip(rows,preds):
        score=prob_temp(pred["scores"],temperature)
        gold=row["nli_relation_oracle"]
        classification=max(score,key=score.get)
        correct.append(int(classification==gold))
        confs.append(max(score.values()))
        brier+=sum((score[label]-(1. if gold==label else 0.))**2
                   for label in ("entailment","neutral","contradiction"))
        nll-=math.log(max(score[gold],1e-12))
    return {"n":len(rows),"relation_accuracy":sum(correct)/len(rows),
        "multiclass_brier":brier/len(rows),
        "negative_log_likelihood":nll/len(rows),
        "top_label_ece":compute_ece(confs,correct)}

def cluster_bootstrap(rows,baseline,hybrid,iterations=3000,seed=20262932):
    import numpy as np
    rng=np.random.default_rng(seed)
    family_to_indices={}
    for ix,r in enumerate(rows):family_to_indices.setdefault(r["scenario_family"],[]).append(ix)
    families=list(sorted(family_to_indices))
    by_metric={"recall":[],"false_positive_rate":[],"precision":[],"f1":[]}
    for _ in range(iterations):
        draw=rng.choice(families,size=len(families),replace=True)
        ix=[i for f in draw for i in family_to_indices[f]]
        sample=[rows[i] for i in ix]
        before=metrics(sample,[baseline[i] for i in ix])
        after=metrics(sample,[hybrid[i] for i in ix])
        for name in by_metric:
            if before[name] is not None and after[name] is not None:
                by_metric[name].append(after[name]-before[name])
    return {"n_bootstrap":iterations,"unit":"synthetic scenario/template family",
        "families":len(families),
        "paired_differences_hybrid_minus_baseline":{
            name:{"estimate":metrics(rows,hybrid)[name]-metrics(rows,baseline)[name],
                  "ci95_descriptive":[float(x) for x in np.quantile(values,[.025,.975])],
                  "valid_draws":len(values)}
            for name,values in by_metric.items() if values
        },
        "interpretation":"Descriptive bootstrap of constructed template families; not a patient-population interval."}

def load_model(cfg):
    import torch
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    modelname=cfg["model"]["id"];revision=cfg["model"]["revision"]
    torch.set_num_threads(2)
    torch.manual_seed(20262932)
    started=time.perf_counter()
    tokenizer=AutoTokenizer.from_pretrained(modelname,revision=revision,trust_remote_code=False)
    model=AutoModelForSequenceClassification.from_pretrained(
        modelname,revision=revision,trust_remote_code=False)
    model.eval()
    labels=[str(model.config.id2label[i]).strip().lower() for i in range(3)]
    assert labels==cfg["model"]["label_mapping_expected"],labels
    assert model.config.num_labels==3
    return torch,tokenizer,model,labels,time.perf_counter()-started

def batch_predictions(keys, cfg, torch, tokenizer, model, labels):
    import psutil
    process=psutil.Process()
    batch_size=12
    outcomes={}
    rss=[process.memory_info().rss];latency=[]
    for start in range(0,len(keys),batch_size):
        part=keys[start:start+batch_size]
        encoding=tokenizer([x[0] for x in part],[x[1] for x in part],
          return_tensors="pt",truncation=True,max_length=cfg["model"]["max_length_tokens"],padding=True)
        begun=time.perf_counter()
        with torch.inference_mode():
            probs=torch.softmax(model(**encoding).logits,dim=-1).cpu().tolist()
        elapsed=(time.perf_counter()-begun)*1000.
        latency.append(elapsed/len(part))
        for key,values in zip(part,probs):
            score={labels[i]:float(x) for i,x in enumerate(values)}
            outcomes[key]={"label":max(score,key=score.get),"scores":score,
                           "batch_forward_avg_ms":elapsed/len(part)}
        rss.append(process.memory_info().rss)
        if (start+len(part))%600<batch_size:
            print("INFERENCE_PROGRESS",start+len(part),"/",len(keys),flush=True)
    return outcomes,{"pairs":len(keys),"batch_size":batch_size,"p50_batch_avg_ms":statistics.median(latency),
                      "p95_batch_avg_ms":sorted(latency)[int(.95*(len(latency)-1))],
                      "max_sampled_RSS_bytes":max(rss),
                      "timing_scope":"Average batch forward/softmax time per pair; excludes tokenization, loading and Python pairing."}

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True)
    args=p.parse_args(); out=args.out;out.mkdir(parents=True,exist_ok=True)
    cfg_path=ROOT/"evaluation"/"masters_nli"/"locked_v2_protocol.json"
    cfg=json.loads(cfg_path.read_text(encoding="utf-8"))
    assert cfg["model"]["revision"]=="6f5cf0a2b59cabb106aca4c287eed12e357e90eb"
    assert cfg["model"]["contradiction_threshold"]==0.5
    assert abs(cfg["model"]["temperature"]-1.8915189348793875)<1e-10
    cfgsha=sha(cfg_path)
    cases=construction()
    data_path=out/"locked_synthetic_280.jsonl"
    dsha=write_jsonl(data_path,cases)
    frozen={"dataset_sha256":dsha,"protocol_sha256":cfgsha,
            "n":len(cases),"timestamp_before_inference":now(),
            "adjudication_status":"pending; author-generated not clinician adjudicated",
            "source_code_commit":os.environ.get("GITHUB_SHA","unknown"),
            "benchmark_locked_pre_inference":True,
            "final_clinical_validation":False,
            "model_checkpoint":cfg["model"]["revision"]}
    dump(out/"PRE_INFERENCE_FREEZE.json",frozen)
    start=time.perf_counter()
    baseline_flags=[bool(compare_facts(extract_facts(r["source_text"]),
                                        extract_facts(r["transformed_text"]))) for r in cases]
    pairing_records=[];all_pairs=set();cases_candidate_records=[]
    for r in cases:
        b1=bidirectional_pairing(r["source_text"],r["transformed_text"],top_k=1)
        b3=bidirectional_pairing(r["source_text"],r["transformed_text"],top_k=3)
        candidates=[]
        for direction in ("transformed_to_source","source_to_transformed"):
            for candidate in b1[direction]:
                # Reference order is specific to each direction; does NOT use gold metadata.
                pair=(candidate.candidate_text,candidate.query_text)
                all_pairs.add(pair)
                candidates.append({"direction":direction,
                    "query_index":candidate.query_index,
                    "candidate_index":candidate.candidate_index,
                    "similarity":candidate.score,"premise":pair[0],"hypothesis":pair[1]})
        recall={}
        for k,reference in [(1,b1),(3,b3)]:
            hits=[]
            if r["target_pair_exists"]:
                si=r["source_target_index"];ti=r["transformed_target_index"]
                for direction in ("transformed_to_source","source_to_transformed"):
                    target=(ti,si) if direction=="transformed_to_source" else (si,ti)
                    hits.append(any((c.query_index,c.candidate_index)==target
                                    for c in reference[direction]))
                recall[str(k)]={"evaluated_pairs":2,"hits":sum(hits)}
            else:
                recall[str(k)]={"evaluated_pairs":0,"hits":0,
                   "unanswerable_due_to_missing_source_or_target":True}
        if r["target_pair_exists"]:
            pair=(r["source_units"][r["source_target_index"]],
                  r["transformed_units"][r["transformed_target_index"]])
            all_pairs.add(pair)
        else:pair=None
        cases_candidate_records.append(candidates)
        pairing_records.append({"id":r["id"],"category":r["drift_category"],
            "gold_direction":r["gold_direction"],"target_pair_exists":r["target_pair_exists"],
            "oracle_pair":pair,
            "target_source_index":r["source_target_index"],
            "target_transformed_index":r["transformed_target_index"],
            "retrieval":{"top1":recall["1"],"top3":recall["3"]}})
    all_pairs=sorted(all_pairs)
    dump(out/"INFERENCE_INPUT_SET_HASH.json",{
      "pair_count":len(all_pairs),
      "pair_set_sha256":hashlib.sha256(json.dumps(all_pairs,ensure_ascii=False).encode()).hexdigest(),
      "model_loaded_after_freeze":True,"retrieval_uses_no_gold_target_index":True})
    print("LOCKED_DATASET",dsha,"N",len(cases),"ALL_MODEL_INPUT_PAIRS",len(all_pairs),flush=True)
    torch, tokenizer, model, labels, load_s=load_model(cfg)
    outcomes,timing=batch_predictions(all_pairs,cfg,torch,tokenizer,model,labels)
    temperature=cfg["model"]["temperature"];threshold=cfg["model"]["contradiction_threshold"]
    combined=[];oracle=[];hybrid_flags=[];review_flags=[]
    evidence_grounded=[];per_case_times=[]
    for r,rule,rec,candidates in zip(cases,baseline_flags,pairing_records,cases_candidate_records):
        case_started=time.perf_counter()
        verdicts=[]
        for c in candidates:
            pred=outcomes[(c["premise"],c["hypothesis"])]
            cal=prob_temp(pred["scores"],temperature)
            is_alert=pred["label"]=="contradiction" and cal["contradiction"]>=threshold
            verdicts.append({**c,"raw_label":pred["label"],"raw_scores":pred["scores"],
                "scaled_scores":cal,"semantic_flag":is_alert})
        ai_flags=[p for p in verdicts if p["semantic_flag"]]
        weak=any(p["similarity"]<0.35 for p in verdicts)
        neutral=any(p["raw_label"]=="neutral" for p in verdicts)
        auto_flag=bool(rule or ai_flags)
        review=bool(auto_flag or weak or neutral)
        hybrid_flags.append(auto_flag);review_flags.append(review)
        aligned=any(p["semantic_flag"] and
                    r["target_pair_exists"] and
                    ((p["direction"]=="transformed_to_source" and
                      p["query_index"]==r["transformed_target_index"] and
                      p["candidate_index"]==r["source_target_index"]) or
                     (p["direction"]=="source_to_transformed" and
                      p["query_index"]==r["source_target_index"] and
                      p["candidate_index"]==r["transformed_target_index"]))
                    and r["nli_relation_oracle"]=="contradiction" for p in ai_flags)
        evidence_grounded.append(aligned)
        if rec["oracle_pair"] is not None:
            oracle_pred=outcomes[tuple(rec["oracle_pair"])]
            oracle.append({"id":r["id"],"category":r["drift_category"],
                           "gold_label":r["nli_relation_oracle"],**oracle_pred})
        combined.append({
            "id":r["id"],"category":r["drift_category"],
            "ground_truth_error_author_constructed":r["integrity_error"],
            "baseline_flag":rule,"hybrid_flag":auto_flag,
            "review_required":review,"weak_pairing":weak,
            "neutral_observed":neutral,"ai_flag_count":len(ai_flags),
            "any_gold_aligned_ai_contradiction":aligned,
            "candidate_predictions":verdicts})
        per_case_times.append((time.perf_counter()-case_started)*1000.)
    write_jsonl(out/"FULL_DOCUMENT_RAW_PREDICTIONS_280.jsonl",combined)
    write_jsonl(out/"ORACLE_TARGET_PREDICTIONS.jsonl",oracle)
    write_jsonl(out/"EVIDENCE_PAIR_RETRIEVAL_280.jsonl",pairing_records)
    write_jsonl(out/"FLAGGED_AND_MISSED_CASES.jsonl",[
         {k:r[k] for k in ("id","category","ground_truth_error_author_constructed",
                          "baseline_flag","hybrid_flag","review_required",
                          "any_gold_aligned_ai_contradiction")}
         for r in combined if (r["ground_truth_error_author_constructed"]!=r["hybrid_flag"])
            or (r["baseline_flag"]!=r["hybrid_flag"])])
    oracle_lookup={r["id"]:r for r in oracle}
    oracle_rows=[r for r in cases if r["id"] in oracle_lookup]
    oracle_predictions=[oracle_lookup[r["id"]] for r in oracle_rows]
    old=metrics(cases,baseline_flags);new=metrics(cases,hybrid_flags)
    pair1=sum(p["retrieval"]["top1"]["hits"] for p in pairing_records)
    pair3=sum(p["retrieval"]["top3"]["hits"] for p in pairing_records)
    paired=2*sum(r["target_pair_exists"] for r in cases)
    by_category={}
    for group in sorted({r["drift_category"] for r in cases}):
        idx=[i for i,r in enumerate(cases) if r["drift_category"]==group]
        by_category[group]={
          "n":len(idx),"truth_errors":sum(cases[i]["integrity_error"] for i in idx),
          "baseline_flags":sum(baseline_flags[i] for i in idx),
          "hybrid_flags":sum(hybrid_flags[i] for i in idx),
          "review_routed":sum(review_flags[i] for i in idx),
          "gold_evidence_aligned_ai_flags":sum(evidence_grounded[i] for i in idx),
        }
    desc=cluster_bootstrap(cases,baseline_flags,hybrid_flags)
    results={
       "status":"LOCKED_BUT_NOT_INDEPENDENTLY_ADJUDICATED_SYNTHETIC_TECHNICAL_TEST",
       "reporting_boundary":"Author-constructed synthetic cases; no independent clinical annotation or patient-outcome evidence.",
       "dataset_sha256":dsha,"protocol_sha256":cfgsha,
       "freeze_record":frozen,
       "source_commit":os.environ.get("GITHUB_SHA","unknown"),
       "model_id":cfg["model"]["id"],
       "model_revision":cfg["model"]["revision"],
       "temperature_scaled_from_prior_development_set":temperature,
       "frozen_contradiction_threshold":threshold,
       "baseline_case_metrics":old,
       "hybrid_case_metrics":new,
       "review_required_n":sum(review_flags),
       "review_burden":sum(review_flags)/len(review_flags),
       "oracle_label_metrics_on_existing_target_pairs":classify_oracle(
          oracle_rows,oracle_predictions,temperature),
       "oracle_target_pair_count":len(oracle_rows),
       "unanswerable_missing_counterpart_case_count":sum(not r["target_pair_exists"] for r in cases),
       "pairing_recall_at_1":pair1/paired,"pairing_recall_at_3":pair3/paired,
       "number_of_evaluable_directional_gold_pairs":paired,
       "gold_aligned_ai_contradiction_case_count":sum(evidence_grounded),
       "extra_hybrid_flagged_case_count":sum(h and not b for h,b in zip(hybrid_flags,baseline_flags)),
       "category_details":by_category,
       "clustered_descriptive_uncertainty":desc,
       "software":{
         "python":platform.python_version(),"torch":torch.__version__,
         "transformers":__import__("transformers").__version__,
         "rapidfuzz":__import__("rapidfuzz").__version__,
         "CPU_cores":os.cpu_count(),"model_load_seconds":load_s,
         "observed_total_experiment_seconds":time.perf_counter()-start,
         "memory":"max sampled resident set, not process peak over all milliseconds",
         "timing":timing,
       },
       "limitations":[
          "Labels are researcher/code generated and all require qualified external adjudication before a final thesis claim.",
          "Even with shuffled positions, scenario templates remain correlated and examples are artificially constructed.",
          "The decision threshold and temperature were fitted on just 28 known development cases with overlapping families.",
          "Subsequent experiments are chronologically after inspecting pilot v1, so no unqualified independent model-selection claim.",
          "The prototype still has no live full-document NLI integration in Streamlit, no deployment privacy assessment.",
          "No clinician effect, patient outcome, medical safety or clinical risk validation.",
          "Review-only ambiguous outputs do not count as automatically detected errors.",
          "NLI evidence-grounded relation must be reported separately from case-level positive flag recall."
       ]
    }
    dump(out/"LOCKED_TECHNICAL_RESULTS.json",results)
    # Verify the benchmark bytes were unchanged throughout model loading and scoring.
    assert sha(data_path)==dsha and sha(cfg_path)==cfgsha
    dump(out/"POST_RUN_INTEGRITY.json",{
       "original_dataset_sha256":dsha,"end_dataset_sha256":sha(data_path),
       "original_protocol_sha256":cfgsha,"end_protocol_sha256":sha(cfg_path),
       "identical_after_inference":True,
       "completed_utc":now()})
    print("LOCKED_TECHNICAL_RESULT",json.dumps({
       "baseline":old,"hybrid":new,"pair_recall_at_1":pair1/paired,
       "pair_recall_at_3":pair3/paired,"oracle_label":results["oracle_label_metrics_on_existing_target_pairs"],
       "review_burden":results["review_burden"],
       "gold_aligned_ai_contradiction":sum(evidence_grounded)},sort_keys=True),flush=True)

if __name__=="__main__":main()
