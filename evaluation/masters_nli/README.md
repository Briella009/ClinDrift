# ClinDrift Master's NLI Evaluation

This directory contains the experimental scaffold for selecting the semantic Natural Language Inference (NLI) component proposed for the master's project:

**Development of an Explainable AI System for Automated Clinical Documentation Integrity Checking**

The purpose of this branch is model selection and evaluation. It does **not** replace the current deterministic ClinDrift baseline and it does not represent a clinically validated system.

## Research question

Does adding a selected NLI semantic-verification layer improve detection of clinically relevant semantic contradictions and source-information preservation failures beyond the deterministic ClinDrift baseline without creating an unacceptable increase in false-positive alerts on meaning-preserving text?

## Why NLI

ClinDrift compares source clinical information with transformed or AI-generated documentation. NLI provides a direct three-way formulation for claim verification:

- **entailment**: the transformed claim is supported by the source;
- **contradiction**: the transformed claim conflicts with the source;
- **neutral**: the source does not provide enough evidence to support or contradict the claim.

This is complementary to ClinDrift's deterministic fact checks rather than a replacement for them.

## Candidate models

The initial comparison deliberately includes both general-domain and biomedical/clinical-domain NLI models.

1. `cross-encoder/nli-deberta-v3-small`
   - general-domain NLI;
   - based on DeBERTa-v3-small;
   - trained on SNLI and MultiNLI;
   - useful as a relatively compact general baseline.

2. `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`
   - broader general/fact-verification NLI training;
   - trained on MultiNLI, FEVER-NLI and ANLI;
   - useful as a stronger general-domain comparator.

3. `pritamdeka/PubMedBERT-MNLI-MedNLI`
   - biomedical/clinical NLI;
   - PubMedBERT fine-tuned on MNLI and then MedNLI;
   - useful for testing whether domain adaptation improves ClinDrift's task.

4. `cross-encoder/nli-MiniLM2-L6-H768`
   - compact non-DeBERTa general-domain comparator;
   - trained on SNLI and MultiNLI;
   - useful for testing whether a smaller architecture offers a better latency/memory trade-off.

No candidate is selected in advance. Model-card scores are **not** treated as evidence of performance on ClinDrift.

## Important dataset caution

MedNLI is clinically relevant and physician-annotated, but published work has shown annotation artifacts and reduced performance on harder adversarial subsets. ClinDrift therefore must not select a model only because it performs well on MedNLI.

The final master's comparison should use a separate frozen ClinDrift held-out benchmark that is not used for prompt/rule/model-selection tuning.

## Evaluation stages

### Stage A - development/regression and model selection

The existing 140-case controlled ClinDrift benchmark is already known to the developer, so it is not treated as one undifferentiated calibration set. Cases are grouped by scenario/template family and used only for development activities such as:
- regression verification of known categories;
- debugging claim construction and evidence retrieval;
- development-only candidate-model comparison;
- threshold/calibration work on a distinct development/calibration partition or resampling scheme.

The NLI models are not fine-tuned on these 140 cases. The same case must not be used simultaneously as the sole basis for model choice, calibration and final performance reporting.

These cases are **not** the final independent performance estimate.

### Stage B - separately generated and frozen held-out benchmark

Before the final model comparison:
- freeze a separate benchmark;
- keep labels unavailable to the scoring logic;
- include both positive drift and meaning-preserving controls;
- include cases outside the deterministic ontology;
- preserve category and severity metadata;
- record the dataset hash.

No model-selection decision should be made from the final held-out scores until all candidate outputs are complete.

## Primary selection criteria

The model should not be selected on accuracy alone.

Primary criteria:
- recall on semantic challenge cases;
- precision / positive predictive value of flagged semantic findings;
- false-positive rate on meaning-preserving controls;
- recall for predeclared critical categories.

Secondary criteria:
- macro F1 and per-class recall/precision;
- Brier score and negative log-likelihood;
- Expected Calibration Error (ECE) plus reliability plots;
- evidence-pairing recall;
- median and p95 latency;
- local memory/storage burden;
- ability to run without sending clinical text to an external API.

Accuracy is reported but is not a headline selection metric because it depends strongly on the constructed class balance.

## Human-review threshold

Low-confidence or ambiguous NLI outputs should be escalated rather than silently accepted.

The final decision threshold will be defined from development data, documented before held-out evaluation, and reported alongside coverage/abstention.

## Explainability

NLI probabilities and source/hypothesis evidence are always shown.

Token-level explanation methods such as SHAP may be evaluated as an additional explanation aid, but they will not be treated as proof that a prediction is correct.

## Deployment

The target research deployment is:
- Streamlit for the examiner/supervisor demonstration;
- Docker for reproducible local execution;
- locally loaded NLI model where feasible;
- no requirement to send clinical text to an external generative-AI API.

## Reproducibility

The evaluation script writes:
- selected model identifier;
- timestamp;
- dataset SHA-256;
- predictions;
- confidence values;
- confusion matrix;
- precision/recall/F1;
- critical contradiction recall when severity metadata is present;
- ECE;
- latency summary.

Synthetic benchmark results must not be described as clinical validation or medical-device performance.


## Bidirectional integrity coverage

ClinDrift does not rely on one transformed-to-source pass.

### Transformed -> source
Each transformed claim is matched against source evidence to identify:
- supported claims (entailment);
- conflicting claims (contradiction);
- possible unsupported additions (neutral/no adequate source support).

### Source -> transformed
Each clinically relevant source claim is matched against transformed documentation to identify:
- preserved information (an entailing transformed match);
- changed information (a contradictory match);
- possible omission (no adequate transformed support).

Neutral does not automatically mean an error. It triggers evidence-search fallback, abstention or human review depending on the pass and available evidence.

## Pairing versus inference

Evidence retrieval/pairing and NLI classification are evaluated separately.

1. **Oracle-pair NLI evaluation:** NLI receives the known relevant source/claim pair.
2. **End-to-end evaluation:** the automatic pairing component selects evidence before NLI.

Pairing recall is reported as the proportion of evaluable cases for which the required evidence is retrieved. This prevents retrieval failures from being misreported as NLI failures.

## Rule-AI reconciliation

The deterministic layer is never silently overridden.

| Deterministic layer | NLI layer | Final handling |
|---|---|---|
| Positive | Agrees | Retain deterministic finding and record AI corroboration |
| Positive | Neutral/disagrees | Retain deterministic finding and record rule-AI discordance for review |
| No supported rule | High-confidence contradiction | Create separately labelled AI semantic finding |
| No supported rule | Low confidence / neutral | Abstain or mark uncertain; do not force an error label |
| Rule says equivalent | NLI contradicts | Record discordance and require review |
| Both show no issue | No issue | No automated finding |

## Explanation boundary

The standard explanation surface is:
- exact evidence pair;
- mechanism provenance (rule or AI);
- calibrated class probabilities/uncertainty;
- model/application version;
- reviewer disposition.

SHAP is optional token-level attribution for selected AI findings. It is not treated as evidence that a prediction is correct or clinically safe.
