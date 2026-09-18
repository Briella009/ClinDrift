# ClinDrift Master's NLI Evaluation

This directory contains the experimental scaffold for selecting the semantic Natural Language Inference (NLI) component proposed for the master's project:

**Development of an Explainable AI System for Automated Clinical Documentation Integrity Checking**

The purpose of this branch is model selection and evaluation. It does **not** replace the current deterministic ClinDrift baseline and it does not represent a clinically validated system.

## Research question

Does adding an NLI semantic-verification layer improve detection of clinically relevant semantic contradiction or unsupported content beyond the deterministic ClinDrift baseline without creating an unacceptable increase in false-positive alerts on meaning-preserving text?

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

No candidate is selected in advance. Model-card scores are **not** treated as evidence of performance on ClinDrift.

## Important dataset caution

MedNLI is clinically relevant and physician-annotated, but published work has shown annotation artifacts and reduced performance on harder adversarial subsets. ClinDrift therefore must not select a model only because it performs well on MedNLI.

The final master's comparison should use a separate frozen ClinDrift held-out benchmark that is not used for prompt/rule/model-selection tuning.

## Evaluation stages

### Stage A - development/regression

Use the existing 140-case controlled ClinDrift benchmark to:
- verify compatibility with known categories;
- identify failure modes;
- debug claim construction;
- tune non-learned decision thresholds where justified.

These cases are **not** the final independent performance estimate.

### Stage B - frozen held-out benchmark

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
- contradiction recall;
- macro F1;
- false-positive rate on meaning-preserving controls;
- critical-error recall on cases labelled critical;
- calibration / Expected Calibration Error (ECE).

Secondary criteria:
- overall accuracy;
- per-class precision and recall;
- median and p95 latency;
- local memory/storage burden;
- ability to run without sending clinical text to an external API.

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
