# ClinDrift Master's Experiment Register — 25 October 2026

**Research branch:** `masters/experiment-evaluation-2026-10-25`  
**Status:** Reproducible synthetic technical studies; **not independently adjudicated, clinically validated, or a final patient-safety claim**.

This directory permanently archives the actual model outputs instead of relying on a GitHub Actions artifact with an expiry date. The original ZIP, the extracted 21 evidence files, the audit, and the separately locked second-wave data and full-document predictions are committed to this branch.

## Experiment ledger

| ID | Experiment | Cases | Status | Key source |
|---|---|---:|---|---|
| E0 | Canonicalised deterministic regression against reconstructed earlier rules | 140 | Completed; developer-known development material | `../../icaiae2026/` |
| E1 | Four NLI checkpoints evaluated for development-only selection | 140 total; 112 selection cases | Completed; template families overlap calibration | `pilot_v1/raw/candidate_status.json` |
| E2 | Temperature fitting and decision-threshold grid | 28 development/calibration cases | Completed; exploratory in-sample fit | `pilot_v1/raw/development_calibration.json` |
| E3 | Target-specified 280-case synthetic pilot | 200 seeded alterations + 80 controls | Completed and independently re-audited from raw predictions; **not full-document retrieval** | `pilot_v1/AUDIT.json` |
| E4 | Separately constructed, pre-inference SHA-256-locked, all-sentence bidirectional synthetic evaluation | 200 seeded alterations + 80 controls | Completed; case labels author-generated, adjudication pending | `locked_v2/LOCKED_TECHNICAL_RESULTS.json` |
| E5 | Structured clinician oversight effectiveness study | — | **Not conducted:** protocol only | `../../human_oversight/PROTOCOL.md` |
| E6 | Accent/code-switching ASR-to-note study | — | **Not conducted:** protocol only | `../../pipeline_integrity/README.md` |

Experiments E3 and E4 deliberately share a common model and calibrated threshold, but not the exact case texts. Both use correlated, researcher-authored synthetic templates. Neither satisfies an external-adjudication or real-patient test.

## E1: All four candidate models — 112-case selection subset

All four NLI checkpoints completed. Results below use the saved **development-selection partition**, not the separate later synthetic benchmark. Model selection combined prespecified development metrics rather than choosing the largest model by default.

| Candidate | NLI relation accuracy | Macro F1 | Semantic challenge auto-recall | Control false-positive rate | Median/p95 timings |
|---|---:|---:|---:|---:|---|
| DeBERTa-v3-small NLI | 91.07% | 0.903 | 87.5% | 0% | CPU in `candidate_status.json` |
| DeBERTa-v3-base MNLI/FEVER/ANLI | **98.21%** | **0.981** | **100%** | 0% | CPU in `candidate_status.json` |
| PubMedBERT-MNLI-MedNLI | 96.43% | 0.960 | 87.5% | 0% | CPU in `candidate_status.json` |
| MiniLM NLI | 95.54% | 0.956 | 100% | 3.13% | CPU in `candidate_status.json` |

Development-selected checkpoint: `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli` at immutable model revision `6f5cf0a2b59cabb106aca4c287eed12e357e90eb`. Selection and calibration case IDs were distinct, but **all 14 template-family IDs occurred in both splits**. This limits claims of model-selection generalization.

## E2: Calibration and threshold

Saved development-only temperature = **1.8915189348793875**; selected contradiction decision threshold = **0.50**. Temperature and threshold were estimated from the same 28 development/calibration cases. They were not re-fitted on E3 or E4 labels, but the limited family overlap and in-sample tuning mean the probabilities are **temperature-scaled, not proven clinically calibrated**.

## E3: Target-specified synthetic pilot — audited historical run

Source commit: `2d412af5d63aec9839fbbebb31c540149e203b56`  
[Original GitHub Actions run](https://github.com/Briella009/ClinDrift/actions/runs/40168975981) · [Verified archive workflow](https://github.com/Briella009/ClinDrift/actions/runs/40171019085)

Original artifact SHA-256: `7d62af4e119f2b8e70ba2965ea68fdef40f44e13a055c042cfa859dabd28068e`

| Outcome on 280 constructed cases | Rules only | Original target-specified hybrid |
|---|---:|---:|
| TP / FP / TN / FN | 120 / 20 / 60 / 80 | 194 / 40 / 40 / 6 |
| Recall | 60% | 97% |
| Precision | 85.71% | 82.91% |
| Control false-positive rate | 25% | 50% |
| F1 | 0.706 | 0.894 |

**Critical corrections to the original pilot interpretation:**

1. Retrieval was supplied the annotated direction and evaluated query index zero. All 280 gold targets were at index zero, with just three candidate sentences. Therefore the reported 100% recall@1 was an *easy target-specified pairing check*, not fully blind document retrieval; recall@3 was exhaustive.
2. Of the 74 additional true-positive *case flags*, **34 had the wrong three-class NLI relation** (neutral unsupported additions were incorrectly called contradictions). Thus case-level flags are not proof of correct semantic explanation.
3. The original case-wise bootstrap interval described flag-rate differences, not recall gain. Synthetic templates are correlated; do not claim patient-population statistical significance from that p-value or interval.
4. The original memory number was a sampled RSS value, not a measured instantaneous peak.
5. The 280 case annotations remained pending, and no human or external checking occurred.

See `pilot_v1/AUDIT.json`, `pilot_v1/raw/`, `pilot_v1/original_artifact.zip`, and `pilot_v1/SHA256SUMS.txt` for every prediction, protocol, condition and checksum.

## E4: Locked all-document synthetic experiment

Run: [Locked GitHub Actions execution](https://github.com/Briella009/ClinDrift/actions/runs/40171220190).  
Source commit: `6d11f007a9e70b254e8d8394ca21f5db992bb99c`.  
Frozen test dataset SHA-256: `a24e6d278d10d3a3f80581edd9cec46165f976a97da5e51ab174b6f29cf147c4`.

The full protocol (`../../masters_nli/locked_v2_protocol.json`) and generator (`../../masters_nli/locked_v2_data.py`) were committed before this run. The system compared **every** sentence, in **both** directions, without passing target locations to retrieval. Source and transformed target locations were shuffled independently. The model checkpoint, temperature, decision threshold (0.50) and lexical top-1 retrieval rule were fixed before scoring. The benchmark and protocol SHA-256 digests were checked again after inference.

| Measure | Unchanged rules only | Fixed hybrid |
|---|---:|---:|
| TP / FP / TN / FN | 40 / 0 / 80 / 160 | 160 / 20 / 60 / 40 |
| Error-case recall | 20.0% | **80.0%** |
| Flagged-case precision | **100.0%** | 88.9% |
| Control false-positive rate | **0.0%** | 25.0% |
| F1 | 0.333 | **0.842** |
| Accuracy | 42.9% | 78.6% |

Additional outcomes: **180/220** (81.8%) correct three-class oracle target-pair labels; temperature-scaled oracle ECE = **0.124** (10 bins); **85.7%** of test cases required reviewer attention; lexical gold-pair recall@1 and recall@3 were both **100%** among 440 directional target matches. Retrieval is still relatively easy because the distractor sentences are shared and the altered target sentence remains lexically similar. There are **60 absent-counterpart cases** for which pair recall is not defined.

**Interpretation:** Hybrid rule-plus-NLI raised synthetic alteration flag recall by **60 percentage points**, but introduced **20 false alerts among 80 meaning-preserving controls**. All 20 new false alerts occurred in the *afebrile versus no fever* control family. The neutral unsupported-diagnosis and unsupported-procedure cases (40 seeded alterations) were **routed for review, not automatically flagged**. Calling them automatically detected errors would be misleading. Correctly aligned contradiction evidence was observed in 140 cases (including cases already detected by rules).

A cluster bootstrap over 14 synthetic scenario/template families gave a **descriptive** 95% interval of **+27.3 to +90.0 percentage points** for recall gain. For the change in false-positive rate, the descriptive interval was **0 to 100 percentage points**, demonstrating the extremely weak precision of inference from so few clustered synthetic families. These intervals do not describe real patient populations.

The local CPU run (4 reported CPU cores) used PyTorch 2.6.0+cpu, Transformers 4.48.3 and RapidFuzz 3.11.0. The record includes a 1,880-pair unique forward evaluation, model and dataset identity, all 280 case-level decisions, all evidence pairs and model scores, all oracle predictions, software package lock, audit checks, descriptive family bootstrap and failures. See `locked_v2/` for the files. Timing is batch-forward timing, not Streamlit or human workflow latency.

## Exactly what can be claimed

**Supported bounded technical finding:** On a separately generated, pre-inference-locked, researcher-authored synthetic 280-case benchmark, the fixed rule-plus-DeBERTa NLI system increased *case-level discrepancy flag recall* from 20% (40/200) to 80% (160/200), while decreasing flagged-case precision from 100% to 88.9% and increasing control false-positive rate from 0% to 25%. This is a sensitivity/specificity trade-off in a constructed evaluation, **not proof of overall clinical superiority**.

**Not supported:** Independent clinical annotation, safe handling of unsupported additions or omissions without human review, patient-safety benefit, a clinically calibrated probability, robust retrieval under realistic note diversity, clinician workload improvement, production deployment, medical-device certification, or generalisation to Nigerian hospital records.

**Required for a definitive final thesis claim beyond the synthetic technical study:** qualified label review/adjudication with a documented protocol; genuinely distinct scenario families and unanswerable retrieval evaluation; development-only refinement to reduce afebrile false alarms without touching locked-test labels; another frozen benchmark after any changes; and review of whether the implemented browser version actually executes the integrated hybrid path. Any changed model, rule or threshold must be registered as a new version, not silently substituted into these experimental results.

## Reproduction and integrity

Run the historical audit without any AI model download:

```bash
python evaluation/masters_nli/archive_and_audit.py
```

For the locked synthetic study (requires network access to the pinned public Hugging Face checkpoint and the pinned environment):

```bash
python evaluation/masters_nli/locked_v2_run.py --out evaluation/experiments/2026-10-25/locked_v2
```

Review `locked_v2/PRE_INFERENCE_FREEZE.json`, `locked_v2/POST_RUN_INTEGRITY.json`, `locked_v2/LOCKED_TECHNICAL_RESULTS.json`, `locked_v2/FULL_DOCUMENT_RAW_PREDICTIONS_280.jsonl`, `locked_v2/EVIDENCE_PAIR_RETRIEVAL_280.jsonl`, `locked_v2/ORACLE_TARGET_PREDICTIONS.jsonl`, and `locked_v2/SHA256SUMS.txt`. The original E3 raw evidence is preserved unchanged. No result is removed when it is unfavourable.
