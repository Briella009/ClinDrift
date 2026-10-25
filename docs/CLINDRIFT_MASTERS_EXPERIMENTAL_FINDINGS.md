# ClinDrift Master's Project: Measured Experimental Findings and Defensible Claim

**Researcher:** Blessing Ezeobioha  
**Project:** Development of an Explainable AI System for Automated Clinical Documentation Integrity Checking  
**Technical test date:** 25 October 2026  
**Research status:** Synthetic engineering results, independently *recomputed from the recorded outputs* but **not independently annotated or clinically validated**.

This is a thesis-supporting technical-evaluation memorandum. It does not automatically replace the school-supervised manuscript or pretend that the required clinical review has happened. The complete dataset, source code, model revision, outputs and reproducibility manifest are in [the experiment register](../evaluation/experiments/2026-10-25/README.md).

## Reproducible implementation and model choice

A four-candidate evaluation was completed using 112 designated development-selection cases from the known 140-case ClinDrift benchmark. The models were:

| Candidate | Correct NLI relation predictions | Three-class accuracy | Macro F1 |
|---|---:|---:|---:|
| DeBERTa-v3-small NLI | 102/112 | 91.07% | 0.903 |
| DeBERTa-v3-base MNLI/FEVER/ANLI | **110/112** | **98.21%** | **0.981** |
| PubMedBERT-MNLI-MedNLI | 108/112 | 96.43% | 0.960 |
| MiniLM2-L6 NLI | 107/112 | 95.54% | 0.956 |

The development-selected checkpoint was `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`, revision `6f5cf0a2b59cabb106aca4c287eed12e357e90eb`. The NLI label mapping was checked explicitly rather than assumed. The calibration fit recorded temperature 1.8915189348793875 and a contradiction flag threshold of 0.50 on 28 designated development cases. Because all 14 template-family IDs overlapped the selection and calibration subsets, the fitted probabilities must not be presented as independently calibrated clinical probabilities.

The earlier 280-case target-specified pilot (E3) gave rules-only TP=120, FN=80, FP=20, TN=60 versus hybrid TP=194, FN=6, FP=40, TN=40, but the audit identified **34 newly flagged positive cases whose inferred NLI relation was wrong**. It also confirmed that gold query indices and directions had been supplied to the retrieval condition; that run must not be described as full-document end-to-end retrieval.

## Second-wave, locked full-document synthetic experiment (E4)

To address those retrieval limitations, a separate 280-case synthetic test was generated from a committed constructor and predeclared protocol. It contained 200 seeded alterations and 80 meaning-preserving controls across 14 scenario families. Five common but independently shuffled context sentences surrounded the target statement. The source/target positions differed across cases. Crucially, retrieval was performed for all source and transformed sentences in both directions, using the text itself and not the annotated target indices.

The model, revision, temperature and 0.50 threshold remained fixed. The benchmark SHA-256 was recorded **before inference**:

`a24e6d278d10d3a3f80581edd9cec46165f976a97da5e51ab174b6f29cf147c4`

The benchmark file and protocol digests were checked again after inference. Source commit: `6d11f007a9e70b254e8d8394ca21f5db992bb99c`. Experiment: [GitHub Actions run 40171220190](https://github.com/Briella009/ClinDrift/actions/runs/40171220190). All raw outputs are available under `evaluation/experiments/2026-10-25/locked_v2/`.

### Primary case-level outcomes

| Metric | Deterministic baseline | Offline rule-plus-NLI hybrid |
|---|---:|---:|
| True positives | 40 | 160 |
| False negatives | 160 | 40 |
| False positives | 0 | 20 |
| True negatives | 80 | 60 |
| Recall on seeded discrepancies | 20.0% | **80.0%** |
| Precision of automated flags | **100.0%** | 88.9% |
| False-positive rate on controls | **0.0%** | 25.0% |
| F1-score | 0.333 | **0.842** |
| Accuracy | 42.9% | 78.6% |

The hybrid increased constructed alteration-case flag recall by **60 percentage points**, but at the cost of a **25-percentage-point increase in control false-positive rate** and an **11.1-percentage-point reduction in precision**. These results establish a genuine trade-off, not unconditional superiority.

The cluster-level bootstrap, resampling the 14 scenario/template families, gave a *descriptive* 95% interval for recall gain of **+27.3 to +90.0 percentage points**. For the control false-positive-rate difference it was **0 to +100 percentage points**, too broad to support any general false-alert guarantee. The constructed cases and repeated templates are not independent patient encounters.

### Error mechanism and limitations

The source-aligned NLI evidence showed 140 detected contradiction cases with a correctly retrieved target relationship; this count includes cases already found by rules and must not be conflated with 140 additional true positives. Oracle three-way NLI relation accuracy was **180/220 (81.8%)** on cases where a true target pair existed. The 10-bin top-label expected calibration error was 0.124, showing non-trivial uncertainty error despite development-fitted temperature scaling.

All **20 false-positive controls** came from the `afebrile_paraphrase_control` family, in which *no fever* and *afebrile* expressed equivalent meaning. The model nevertheless flagged a contradiction. In the 40 unsupported-diagnosis and unsupported-procedure cases, the system routed cases to human review but did **not** issue automated error flags; treating them as detected errors would inflate the result.

Evidence-pair recall@1 and @3 was 100% among 440 evaluable directional target matches. However, the background sentences were identical across source and transformed versions and the targets remained lexically similar. Therefore the high pairing score does **not** prove reliability on realistic long notes, hard distractors or clinically ambiguous evidence. The 60 no-counterpart cases were correctly excluded from pair recall rather than assigned a perfect score.

The review-required rate was **240/280 (85.7%)**. This is a routing measure, not proof that a clinician would process those cases correctly or efficiently. The measured benchmark ran offline; integration of the selected NLI path into the ordinary Streamlit review screen and formal human evaluation are not established by this run.

## Thesis-ready result and conclusion paragraph

On a pre-inference-locked, researcher-constructed benchmark of 280 synthetic clinical-documentation transformations, comprising 200 seeded integrity alterations and 80 meaning-preserving controls, the fixed offline ClinDrift hybrid increased automated discrepancy-case recall from 20.0% (40/200) with the deterministic baseline to 80.0% (160/200). This improvement was accompanied by a decline in flagged-case precision from 100.0% to 88.9% and an increase in control false-positive rate from 0.0% to 25.0%. The hybrid achieved an F1-score of 0.842 compared with 0.333 for the deterministic baseline, but it also routed 85.7% of cases for review. The major false-positive failure occurred when *no fever* was paraphrased as *afebrile*; neutral unsupported additions were reviewed rather than automatically verified as errors. The results demonstrate that a bounded NLI extension can broaden contradiction flagging in this constructed, text-only technical experiment, while also introducing clinically relevant risks of false alarms and review burden. The benchmark was separately generated, hashed before inference and evaluated with an unchanged model and decision threshold, but the cases were researcher-authored and have not been independently adjudicated. Accordingly, these results support a reproducible proof of technical feasibility and a clearly measured sensitivity–false-alert trade-off. They do not establish clinical validity, patient-safety benefit, deployment readiness or generalisation to real hospital records.

## What must be done before describing this as a definitive final validation

1. Have suitably qualified second-person reviewers check all 280 cases, especially clinical equivalence, omitted relevance and any unsupported diagnosis/procedure labels. Record their independent labels and disagreements rather than retroactively marking generated labels as adjudicated.
2. Build a more challenging evidence-retrieval set with *non-identical* distractors, misleading overlaps, unmatched candidates, multi-sentence claims and source/transformed texts that are not simple templated variants.
3. Revise the handling of afebrile equivalence and neutral unsupported additions using **new development data only**, not the frozen test labels; then evaluate any new version on another test set with a new SHA-256.
4. Demonstrate the full semantic inference path in the Streamlit application and re-run application tests, latency/resource measurements, privacy checks and report-export checks on the release version.
5. For a claim about human oversight effectiveness, conduct the specified participant study with appropriate permissions and qualified review; the current study has not done that.

The examiner should be shown the negative findings as well as the improvements. A technically honest conclusion does not require a perfect model or an invented success rate.
