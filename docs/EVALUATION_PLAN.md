# ClinDrift Evaluation Plan

## Experimental Evaluation Plan for Clinically Significant Information Drift Detection

**Project:** ClinDrift  
**Version:** v0.1  
**Status:** Research Prototype  
**Repository:** https://github.com/Briella009/ClinDrift

---

## 1. Purpose

This document defines the evaluation plan for ClinDrift v0.1.

ClinDrift is an open-source research prototype designed to detect selected forms of clinically significant information drift between source clinical information and transformed or AI-generated clinical text.

The purpose of this evaluation is to determine how reliably the current prototype detects the specific forms of information drift that it claims to support.

The central evaluation question is:

> **How accurately and consistently does ClinDrift detect supported forms of clinical information drift under controlled experimental conditions?**

This evaluation does not attempt to establish clinical safety, clinical effectiveness, medical-device performance, or regulatory compliance.

---

## 2. Evaluation Scope

The v0.1 evaluation will focus only on functionality that is currently implemented.

The primary evaluated categories are:

1. medication dosage drift;
2. allergy contradiction;
3. duration drift;
4. no-drift controls.

The evaluation will also examine:

- evidence traceability;
- severity consistency;
- integrity-score behaviour;
- false-positive behaviour;
- controlled mutation detection;
- reproducibility.

The following planned capabilities are excluded from current v0.1 performance claims:

- general negation drift;
- laterality drift;
- medication-frequency drift;
- advanced measurement drift;
- unsupported additions;
- clinically significant omission detection;
- prompt-injection detection;
- privacy-leakage detection;
- FHIR integration;
- comprehensive clinical NLP.

---

## 3. Evaluation Questions

### EQ1

Can ClinDrift detect medication dosage changes between source and transformed clinical text?

### EQ2

Can ClinDrift detect contradictions involving documented medication allergies?

### EQ3

Can ClinDrift detect changes in symptom or treatment duration?

### EQ4

Can ClinDrift avoid reporting drift when supported information remains unchanged?

### EQ5

Does ClinDrift attach the correct source and transformed evidence to detected findings?

### EQ6

Are severity labels applied consistently for equivalent drift categories?

### EQ7

Does the integrity score respond consistently when supported drift is introduced?

### EQ8

Does the controlled Mutation Lab generate reproducible mutations that are subsequently detected by the ClinDrift integrity engine?

---

## 4. Evaluation Design

ClinDrift v0.1 will initially be evaluated using synthetic source-transformation pairs.

Each evaluation case will contain:

- a unique case identifier;
- source clinical text;
- transformed clinical text;
- expected drift category;
- source value;
- transformed value;
- expected detection outcome;
- expected severity where applicable;
- expected evidence;
- actual ClinDrift result.

Ground truth must be defined before ClinDrift processes each evaluation case.

The high-level evaluation flow is:

```text
Synthetic source record
        ↓
Controlled transformation
        ↓
Predefined ground truth
        ↓
ClinDrift analysis
        ↓
Detected findings
        ↓
Evidence + severity + integrity score
        ↓
Comparison with ground truth
        ↓
Performance metrics
        ↓
Error analysis
```

---

## 5. Evaluation Dataset

The initial benchmark will use synthetic clinical information rather than identifiable patient records.

The proposed first benchmark will contain approximately **150 source-transformation pairs**.

| Category | Planned Cases |
| --- | ---: |
| Dosage drift | 30 |
| Allergy contradiction | 30 |
| Duration drift | 30 |
| No-drift controls | 45 |
| Multi-mutation cases | 15 |
| **Total** | **150** |

The final number may change during benchmark construction if additional cases are needed to represent edge conditions.

Any change to benchmark size or category distribution must be documented.

---

## 6. Why Synthetic Data Will Be Used

Synthetic information is appropriate for the first ClinDrift evaluation because it allows:

- exact ground-truth definition;
- controlled manipulation of clinical facts;
- reproducible experiments;
- public sharing of examples;
- reduced privacy risk;
- avoidance of identifiable patient data;
- systematic creation of edge cases;
- controlled comparison between expected and detected results.

Performance on synthetic records does not establish performance on real-world clinical documentation.

Real-world evaluation would require a separate study.

---

## 7. Benchmark Version

The initial benchmark should be named:

**ClinDrift Synthetic Benchmark v0.1**

Software and benchmark versions must be tracked independently.

For example:

```text
ClinDrift software: v0.1
Benchmark: ClinDrift Synthetic Benchmark v0.1
```

If cases are added, removed, materially changed, or corrected, the benchmark version should be updated.

---

## 8. Case Identifier Convention

Each benchmark case should receive a unique identifier.

Recommended formats:

```text
CD-DOSE-001
CD-DOSE-002

CD-ALLERGY-001
CD-ALLERGY-002

CD-DURATION-001
CD-DURATION-002

CD-CONTROL-001
CD-CONTROL-002

CD-MULTI-001
CD-MULTI-002
```

The identifier should remain linked to:

- source text;
- transformed text;
- ground truth;
- ClinDrift output;
- metric calculations;
- error analysis.

---

## 9. Ground-Truth Schema

Each benchmark case should contain structured ground truth.

Recommended fields:

```text
case_id
category
source_text
transformed_text
expected_drift
source_value
transformed_value
expected_severity
expected_detection
notes
```

Example:

```text
case_id: CD-DOSE-001
category: dosage
expected_drift: Dosage drift
source_value: 500 mg
transformed_value: 1000 mg
expected_severity: Critical
expected_detection: True
```

Ground truth must be written before the case is analysed.

This prevents evaluation labels from being adjusted after seeing ClinDrift's result.

---

## 10. Evaluation Output Schema

For each benchmark case, the evaluation should record:

```text
case_id
expected_drift
detected_drift
expected_detection
actual_detection
source_value
detected_source_value
transformed_value
detected_transformed_value
expected_severity
detected_severity
source_evidence_correct
transformed_evidence_correct
integrity_score
review_status
evaluation_outcome
failure_type
notes
```

These fields will support later quantitative and qualitative analysis.

---

## 11. Dosage Drift Evaluation

Dosage-drift cases will contain a medication dose in the source text and a deliberately changed dose in the transformed text.

Example:

### Source

`Patient takes metformin 500 mg twice a day.`

### Transformed

`Patient takes metformin 1000 mg twice a day.`

### Ground Truth

`Dosage drift`

Expected ClinDrift behaviour:

- detect dosage drift;
- identify the original dosage;
- identify the transformed dosage;
- preserve source evidence;
- preserve transformed evidence;
- classify severity according to the implemented v0.1 rule;
- reduce the integrity score appropriately;
- trigger human review where required.

---

## 12. Dosage Drift Variations

The benchmark should use multiple values rather than repeating one example.

Possible synthetic transformations include:

```text
250 mg → 500 mg
500 mg → 1000 mg
10 mg → 20 mg
20 mg → 40 mg
5 mg → 10 mg
25 mg → 50 mg
```

These examples are synthetic information-integrity cases.

They are not treatment recommendations and must not be interpreted as prescribing guidance.

Future evaluation may also consider:

- decimal values;
- unit changes;
- equivalent unit conversions;
- medication-frequency changes.

Equivalent unit conversion is outside the current v0.1 scope unless explicitly implemented.

---

## 13. Allergy Contradiction Evaluation

Allergy cases will contain explicit allergy information in the source and contradictory information in the transformed record.

Example:

### Source

`Patient is allergic to penicillin.`

### Transformed

`No known drug allergies.`

### Ground Truth

`Allergy contradiction`

Expected behaviour:

- contradiction detected;
- allergy value identified;
- source evidence preserved;
- transformed evidence preserved;
- critical severity applied according to current prototype rules;
- human review triggered.

---

## 14. Allergy Variation

Synthetic cases should vary:

- medication names;
- sentence position;
- surrounding information;
- wording of allergy statements.

Examples may include:

`Patient is allergic to penicillin.`

`Penicillin allergy documented.`

`Known allergy: penicillin.`

The objective is to evaluate preservation of the allergy fact rather than exact sentence matching.

---

## 15. Duration Drift Evaluation

Duration-drift cases will alter a supported duration expression.

Example:

### Source

`Patient reports headaches for 3 days.`

### Transformed

`Patient reports headaches for 3 weeks.`

### Ground Truth

`Duration drift`

Expected behaviour:

- detect duration drift;
- identify source duration;
- identify transformed duration;
- preserve evidence;
- assign severity consistently;
- update the integrity score.

---

## 16. Duration Variations

Potential synthetic cases include:

```text
2 days → 2 weeks
3 days → 3 weeks
5 days → 5 weeks
7 days → 7 weeks
```

Later work may evaluate equivalent expressions such as:

```text
7 days = 1 week
```

However, semantic-equivalence reasoning should not be claimed until implemented and evaluated.

---

## 17. No-Drift Controls

No-drift cases are essential.

A detector that flags every comparison could appear to have high recall but would be practically unusable.

Control cases will therefore contain source and transformed information where supported facts remain unchanged.

Example:

### Source

`Blood pressure is 122/78.`

### Transformed

`Blood pressure is 122/78.`

Expected result:

`No supported drift detected.`

---

## 18. Meaning-Preserving Controls

Where the current extraction logic supports it, some control cases should contain minor linguistic changes while preserving the same fact.

Example:

### Source

`Patient takes metformin 500 mg twice a day.`

### Transformed

`The patient takes metformin 500 mg twice a day.`

Expected result:

`No dosage drift.`

These cases help evaluate whether ClinDrift responds to clinical values rather than harmless formatting differences.

---

## 19. Multi-Mutation Cases

A smaller group of benchmark cases will contain multiple controlled mutations.

Example:

### Source

```text
Patient reports headaches for 3 days.
Patient is allergic to penicillin.
Patient takes metformin 500 mg twice a day.
```

### Transformed

```text
Patient reports headaches for 3 weeks.
No known drug allergies.
Patient takes metformin 1000 mg twice a day.
```

Ground truth:

- duration drift;
- allergy contradiction;
- dosage drift.

Expected behaviour:

ClinDrift should independently detect all currently supported mutations.

---

## 20. Current Mutation Lab Baseline

The current ClinDrift Mutation Lab introduces three controlled mutations:

1. dosage drift;
2. allergy contradiction;
3. duration drift.

The current demonstration has produced:

```text
Injected mutations: 3
Detected mutations: 3
Controlled mutation detection rate: 100%
```

This means only that ClinDrift detected the three mutations generated by the current built-in demonstration.

It does not establish:

- 100% clinical accuracy;
- 100% recall on real records;
- 100% sensitivity;
- generalisability;
- regulatory validation;
- clinical validation.

The larger benchmark is required before broader performance statements are made.

---

## 21. Outcome Classification

Each expected event will be classified using standard outcomes.

### True Positive

A supported mutation exists and ClinDrift detects it correctly.

### False Positive

No corresponding supported mutation exists but ClinDrift reports one.

### True Negative

No supported mutation exists and ClinDrift correctly reports no corresponding drift.

### False Negative

A supported mutation exists but ClinDrift does not detect it.

---

## 22. Confusion Matrix

Aggregate performance may be represented as:

| | Predicted Drift | Predicted No Drift |
| --- | ---: | ---: |
| Actual Drift | True Positive | False Negative |
| Actual No Drift | False Positive | True Negative |

This provides the foundation for precision, recall, F1 score, and false-positive analysis.

---

## 23. Precision

Precision answers:

> Of the drift findings ClinDrift reported, how many were correct?

Formula:

```text
Precision = TP / (TP + FP)
```

High precision indicates fewer unnecessary alerts.

This matters because excessive false findings may increase reviewer burden and reduce confidence in the assurance process.

---

## 24. Recall

Recall answers:

> Of all known supported drift events, how many did ClinDrift detect?

Formula:

```text
Recall = TP / (TP + FN)
```

Recall is particularly important for an assurance system because missed clinically significant changes represent undetected integrity failures.

---

## 25. F1 Score

The F1 score combines precision and recall.

```text
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

F1 should be calculated:

- overall;
- by supported drift category where appropriate.

---

## 26. False-Positive Rate

No-drift control cases will be used to assess unnecessary findings.

Formula:

```text
False Positive Rate = FP / (FP + TN)
```

A high false-positive rate may reduce usefulness even if recall is high.

---

## 27. False-Negative Rate

The false-negative rate reflects supported drift events that were missed.

```text
False Negative Rate = FN / (FN + TP)
```

Every false negative should receive qualitative error analysis.

---

## 28. Category-Level Performance

Aggregate metrics may hide weaknesses in specific drift rules.

Performance should therefore be reported separately for each category.

Example future results table:

| Category | Cases | TP | FP | FN | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dosage drift | 30 | TBD | TBD | TBD | TBD | TBD | TBD |
| Allergy contradiction | 30 | TBD | TBD | TBD | TBD | TBD | TBD |
| Duration drift | 30 | TBD | TBD | TBD | TBD | TBD | TBD |
| Controls | 45 | N/A | TBD | N/A | N/A | N/A | N/A |

All values remain `TBD` until the benchmark is actually executed.

---

## 29. Evidence Accuracy

ClinDrift's intended contribution includes evidence traceability.

Evaluation must therefore examine not only whether a drift type is detected, but whether the evidence is correct.

For each true-positive finding, assess:

1. Was the correct source value identified?
2. Was the correct transformed value identified?
3. Was the correct source evidence presented?
4. Was the correct transformed evidence presented?
5. Does the rationale correspond to the actual mutation?

A finding with the correct category but incorrect supporting evidence should be recorded as an evidence failure.

---

## 30. Evidence Accuracy Metric

A simple future metric may be:

```text
Evidence Accuracy =
Correctly evidenced true-positive findings
/
Total true-positive findings
```

More detailed evaluation may report source-evidence and transformed-evidence accuracy separately.

---

## 31. Severity Consistency

Severity classification should be deterministic for equivalent findings.

The evaluation should confirm that equivalent examples of:

- dosage drift;
- allergy contradiction;
- duration drift

receive consistent severity under the same rule set.

This evaluates software consistency.

It does not establish that the severity classification is clinically validated.

Clinical validation would require independent expert assessment.

---

## 32. Integrity Score Evaluation

The integrity score should be evaluated for internal consistency.

Questions include:

- Does a clean case produce the intended high score?
- Does introduction of supported drift reduce the score?
- Do critical findings influence the score as designed?
- Are identical findings scored identically?
- Do multiple findings produce consistent score behaviour?

The integrity score remains an experimental assurance measure.

It is not a probability of patient harm.

---

## 33. Human Review Evaluation

The application should retain human review when safety-relevant findings are detected.

For each benchmark case, record:

- review status;
- number of critical findings;
- risk level where displayed;
- whether the status is consistent with current scoring logic.

No automated status should claim that a clinical record is medically safe.

Even when no supported drift is detected, the application should preserve the boundary that clinical verification remains necessary.

---

## 34. Benchmark Execution Procedure

For each benchmark case:

1. confirm the ClinDrift version;
2. record the Git commit;
3. load the source record;
4. load the transformed record;
5. confirm predefined ground truth;
6. run ClinDrift;
7. record detected findings;
8. record evidence;
9. record severity;
10. record integrity score;
11. record review status;
12. compare detected findings with expected findings;
13. classify the outcome;
14. store the result.

The same procedure should be followed for every case.

---

## 35. Automated Testing Before Benchmarking

Before running a formal benchmark, execute:

```text
python -m pytest -v
```

The current v0.1 test suite contains four core tests covering:

- dosage drift detection;
- preserved measurement behaviour;
- allergy contradiction detection;
- duration drift detection.

Formal benchmark execution should not proceed if previously passing tests unexpectedly fail.

---

## 36. Current Automated Test Baseline

The current prototype baseline is:

```text
4 passed
```

This confirms the implemented unit tests pass.

It does not establish benchmark performance or clinical validity.

---

## 37. Reproducibility Information

Each formal experiment should record:

```text
Project: ClinDrift
Software version: v0.1
Git commit: <commit-hash>
Benchmark: ClinDrift Synthetic Benchmark v0.1
Python version: <version>
Case count: <number>
Evaluation date: <date>
```

Dependency versions should also be preserved through `requirements.txt`.

---

## 38. Determinism Evaluation

ClinDrift v0.1 is intended to behave deterministically.

Selected benchmark cases should therefore be executed repeatedly.

For identical inputs, compare:

- detected findings;
- severity;
- source evidence;
- transformed evidence;
- integrity score;
- review status.

Expected behaviour:

```text
Identical input produces identical output.
```

Any unexpected variation should be investigated.

---

## 39. Mutation Reproducibility

The Mutation Lab should produce repeatable controlled mutations.

For a fixed supported source record:

1. generate controlled drift;
2. record mutations;
3. reset;
4. repeat the mutation;
5. compare results.

The same deterministic mutation function should produce the same output for the same input.

---

## 40. Multi-Mutation Metrics

Multi-mutation cases require additional reporting.

### Complete Detection

All expected supported mutations in the case are identified.

### Partial Detection

At least one expected mutation is identified, but one or more are missed.

### Complete Miss

None of the expected supported mutations are identified.

A future metric may report:

```text
Complete Multi-Mutation Detection Rate
```

and

```text
Partial Multi-Mutation Detection Rate
```

---

## 41. Benchmark Diversity

The benchmark should avoid repeating exactly the same sentence template.

Variation should include:

- sentence order;
- punctuation;
- medication names;
- different dosage values;
- different duration values;
- surrounding irrelevant information;
- simple wording changes.

However, the v0.1 benchmark should remain within the capabilities being evaluated.

A separate robustness benchmark should later test more difficult language.

---

## 42. Development and Evaluation Separation

As the benchmark grows, examples used to modify detection logic should be separated from final evaluation examples.

A future split may use:

```text
Development set: 30%
Held-out evaluation set: 70%
```

Rules may be refined on the development set.

Reported final performance should then come from the held-out set.

---

## 43. Test Leakage

Final evaluation examples should not simply duplicate:

- unit-test sentences;
- Mutation Lab development examples;
- examples used to tune regex rules.

The held-out benchmark should contain new formulations.

This reduces the risk of overstating performance through evaluation on memorised patterns.

---

## 44. Error Analysis

Every false positive and false negative should be reviewed.

For each failure, record:

```text
case_id
expected_result
detected_result
failure_type
probable_cause
affected_component
recommended_action
```

Potential causes include:

- extraction failure;
- comparison failure;
- pattern limitation;
- concept-matching failure;
- unexpected formatting;
- unsupported language;
- unsupported drift type;
- incorrect ground truth.

---

## 45. Failure Taxonomy

Failures should be classified consistently.

### Extraction Failure

A relevant clinical concept was not extracted correctly.

### Comparison Failure

The required values were extracted but compared incorrectly.

### Detection Failure

The difference was available but the rule failed to flag it.

### False Positive

Preserved information was incorrectly identified as drift.

### Evidence Failure

The drift category was correct but supporting evidence was incorrect.

### Severity Failure

The drift was correctly identified but assigned an unexpected severity.

### Unsupported Case

The case contains a form of drift not implemented in v0.1.

### Ground-Truth Error

The benchmark label itself is incorrect.

---

## 46. Robustness Evaluation

After the primary benchmark, robustness testing may vary formatting while preserving clinical meaning.

Examples include:

- uppercase/lowercase changes;
- punctuation differences;
- sentence-order changes;
- whitespace changes;
- decimal formatting;
- abbreviations;
- alternative duration formatting.

The purpose is to identify dependence on formatting rather than clinically relevant values.

---

## 47. Boundary Cases

Future boundary cases may include:

```text
5 mg vs 5.0 mg
500 mg vs 0.5 g
7 days vs 1 week
```

These examples introduce equivalence reasoning.

ClinDrift should not claim to handle them until corresponding normalization logic exists and has been tested.

---

## 48. Baseline Comparison

After the synthetic benchmark is established, ClinDrift should eventually be compared against baseline approaches.

Potential baselines include:

### Exact Text Equality

Reports a difference whenever text is not identical.

Likely limitation:

Harmless paraphrasing may be treated as an error.

### Token Similarity

Measures lexical overlap.

Likely limitation:

A clinically important numeric change may occur inside otherwise highly similar text.

### Semantic Similarity

Measures general semantic similarity.

Likely limitation:

Overall semantic similarity may remain high despite a dangerous local change.

### Embedding Similarity

Represents text as vectors and compares distance.

Likely limitation:

Local clinically significant changes may be diluted within document-level similarity.

### LLM Reviewer

Uses a generative model to judge whether information changed.

Potential advantages:

- flexible language understanding.

Potential limitations:

- non-determinism;
- hallucination;
- cost;
- privacy;
- interpretability;
- dependency on an external model.

ClinDrift should be evaluated against such approaches rather than assumed to be superior.

---

## 49. Real AI Transformation Phase

Synthetic mutation testing represents controlled evaluation.

A later phase may evaluate transformations generated by real AI systems.

Possible tasks include:

- clinical summarisation;
- AI scribing;
- discharge-summary generation;
- patient-summary generation;
- note condensation;
- structured-to-text generation.

These transformations may introduce unpredictable errors.

Ground truth would therefore require independent annotation.

---

## 50. Human Annotation

For future uncontrolled AI transformations, independent reviewers should determine whether clinically important information changed.

An annotation protocol should define:

- drift categories;
- category definitions;
- examples;
- exclusion criteria;
- uncertainty handling;
- disagreement resolution.

Where feasible, more than one independent reviewer should annotate cases.

---

## 51. Inter-Rater Agreement

If multiple reviewers annotate the same cases, agreement may be measured using an appropriate statistic such as:

- percent agreement;
- Cohen's kappa;
- Fleiss' kappa.

The measure selected should reflect the number of reviewers and annotation design.

---

## 52. Security Evaluation Roadmap

Security-focused evaluation is planned for later versions.

Potential experiments may include:

- indirect prompt-injection contamination;
- malicious instructions embedded in source text;
- clinical-data manipulation;
- evidence tampering;
- integrity-score tampering;
- provenance alteration;
- privacy-leakage indicators.

These capabilities are planned research areas and must not be presented as implemented in v0.1.

---

## 53. Privacy Evaluation

The v0.1 benchmark should use synthetic information only.

Public benchmark cases should not contain:

- real patient names;
- hospital numbers;
- phone numbers;
- addresses;
- real medical-record identifiers;
- identifiable medical histories.

Before committing benchmark files to GitHub, inspect them for sensitive information.

---

## 54. Repository Safety

Before adding evaluation data to the public repository:

1. confirm data are synthetic or properly approved;
2. inspect files for identifiers;
3. confirm private-data directories remain ignored;
4. review `git status`;
5. confirm no API keys exist;
6. confirm no passwords or tokens exist;
7. confirm no local secrets are staged.

---

## 55. Proposed Benchmark Storage

The future benchmark may use:

```text
data/
└── benchmark/
    ├── benchmark_v0.1.json
    ├── ground_truth_v0.1.json
    └── README.md
```

This structure is planned.

It should not be described as implemented until those files actually exist.

---

## 56. Proposed Evaluation Infrastructure

Future automated benchmark evaluation may use:

```text
evaluation/
├── run_benchmark.py
├── metrics.py
├── error_analysis.py
└── results/
```

Potential outputs may include:

```text
results_summary.json
results_by_case.csv
metrics.json
error_analysis.csv
```

Again, these are planned components, not current v0.1 functionality.

---

## 57. Statistical Reporting

Formal results should include raw counts and derived metrics.

Example:

| Metric | Result |
| --- | ---: |
| Total cases | TBD |
| True positives | TBD |
| False positives | TBD |
| True negatives | TBD |
| False negatives | TBD |
| Precision | TBD |
| Recall | TBD |
| F1 | TBD |
| False-positive rate | TBD |

Do not insert values until the benchmark has actually been executed.

---

## 58. Integrity Score Reporting

Future evaluation should report integrity-score distributions for:

- clean controls;
- single high-severity drift;
- single critical drift;
- multiple-drift cases.

Possible descriptive statistics include:

- mean;
- median;
- minimum;
- maximum;
- standard deviation.

The purpose is to understand scoring behaviour, not to estimate medical risk.

---

## 59. Evidence Reporting

Potential evidence metrics include:

| Evidence Measure | Result |
| --- | ---: |
| Correct source value | TBD |
| Correct transformed value | TBD |
| Correct source evidence | TBD |
| Correct transformed evidence | TBD |
| Complete evidence traceability | TBD |

This supports evaluation of ClinDrift's transparency objective.

---

## 60. Claim Discipline

Research claims must remain proportional to the evidence.

### Appropriate Current Claim

> ClinDrift detected all three deliberately introduced mutations in its built-in v0.1 controlled demonstration.

### Inappropriate Claim

> ClinDrift is 100% accurate.

### Appropriate Future Benchmark Claim

> ClinDrift achieved X precision, Y recall, and Z F1 score on the ClinDrift Synthetic Benchmark v0.1 under the documented experimental conditions.

### Inappropriate Future Claim

> ClinDrift prevents medical errors.

The evaluation plan intentionally separates technical evidence from unsupported clinical claims.

---

## 61. Safety Interpretation

ClinDrift evaluates fidelity between source and transformed information.

It does not determine whether the original source information itself is clinically correct.

For example:

```text
Source:
Medication A 500 mg

Transformed:
Medication A 500 mg
```

ClinDrift may report that the dosage was preserved.

That does not establish that `500 mg` is medically appropriate.

ClinDrift evaluates transformation integrity, not treatment correctness.

---

## 62. Threats to Internal Validity

Potential threats include:

- incorrect benchmark labels;
- implementation bugs;
- mutation-generation errors;
- evaluation-code bugs;
- leakage between development and evaluation examples;
- inconsistent software versions.

Mitigation includes:

- predefined ground truth;
- unit testing;
- version control;
- held-out evaluation;
- manual benchmark inspection;
- reproducible scripts.

---

## 63. Threats to External Validity

Results from synthetic records may not generalise directly to:

- real EHR data;
- different clinical specialties;
- very long clinical narratives;
- multilingual records;
- noisy clinical notes;
- unusual medication terminology;
- different healthcare systems;
- different AI transformation products.

Real-world generalisation must therefore be evaluated separately.

---

## 64. Threats to Construct Validity

Clinical information drift is broader than the current three implemented categories.

Important future categories may include:

- diagnosis omission;
- general negation reversal;
- laterality errors;
- temporal-order changes;
- medication-frequency changes;
- procedure changes;
- identity confusion;
- unsupported clinical additions.

Therefore v0.1 performance should be described as performance on the evaluated drift categories, not clinical information integrity in general.

---

## 65. Ethical Considerations

The initial benchmark uses synthetic information to reduce ethical and privacy risk.

ClinDrift should not be evaluated prospectively on patient care during this prototype phase.

Future research involving real patient information or clinical personnel may require:

- institutional approval;
- ethics review;
- privacy assessment;
- information-governance approval;
- security assessment;
- data-processing agreements.

---

## 66. Acceptance Criteria for the v0.1 Research Evaluation

The v0.1 benchmark phase can be considered complete when:

- the benchmark has been constructed;
- every case has predefined ground truth;
- the benchmark is versioned;
- automated tests pass;
- all benchmark cases have been executed;
- precision has been calculated;
- recall has been calculated;
- F1 has been calculated;
- false positives have been analysed;
- false negatives have been analysed;
- evidence accuracy has been evaluated;
- scoring behaviour has been evaluated;
- results have been reproduced;
- limitations have been documented.

These conditions indicate completion of a research evaluation.

They do not establish clinical readiness.

---

## 67. Evaluation Roadmap

### Stage 1 — Current v0.1

Completed:

- functioning prototype;
- three controlled mutation types;
- 3/3 controlled demonstration detection;
- four passing core tests;
- evidence traceability;
- severity classification;
- integrity scoring;
- human-review status;
- downloadable audit report;
- research documentation.

### Stage 2 — Synthetic Benchmark

Next:

- create approximately 150 cases;
- define ground truth;
- automate benchmark execution;
- calculate performance metrics;
- conduct error analysis.

### Stage 3 — Expanded Drift Taxonomy

Planned:

- negation drift;
- laterality drift;
- medication-frequency drift;
- measurement drift;
- unsupported additions;
- clinically important omissions.

### Stage 4 — Security Assurance

Planned:

- prompt-injection testing;
- malicious source instructions;
- information manipulation;
- evidence tampering;
- privacy-leakage indicators.

### Stage 5 — Independent AI Transformations

Planned:

- evaluate external AI-generated records;
- independently annotate errors;
- compare against baseline approaches.

---

## 68. Expected Research Outputs

The evaluation may eventually support:

- technical reports;
- research posters;
- conference demonstrations;
- conference papers;
- journal manuscripts;
- open-source research artefacts;
- PhD research discussions;
- reproducibility packages.

The value of these outputs should come from the evaluation evidence, not simply from the existence of the Streamlit interface.

---

## 69. Current Evidence Boundary

ClinDrift currently has evidence to state that:

- a functioning open-source v0.1 prototype exists;
- dosage drift detection is implemented;
- allergy contradiction detection is implemented;
- duration drift detection is implemented;
- the built-in three-mutation demonstration is detected 3/3;
- four automated core tests pass;
- evidence is shown for findings;
- an integrity score is generated;
- human review is retained;
- an audit report can be downloaded.

ClinDrift does **not yet** have evidence to state that:

- it has validated real-world clinical accuracy;
- it works across all medical documentation;
- it prevents patient harm;
- it outperforms commercial or academic systems;
- it is clinically validated;
- it meets regulatory requirements;
- it is a medical device;
- it achieves 100% accuracy.

---

## 70. Final Evaluation Principle

The ClinDrift evaluation follows one core principle:

> **Define the expected result before testing, measure what the software actually does, preserve evidence of failure as well as success, and never make a stronger claim than the experiment supports.**

This principle is intended to keep ClinDrift transparent, reproducible, scientifically defensible, and appropriate for trustworthy-AI research.

---

## Disclaimer

ClinDrift is an experimental research prototype intended for controlled research, software testing, education, and academic experimentation.

ClinDrift has not been clinically validated and must not be used independently for diagnosis, treatment, medication management, patient monitoring, or autonomous clinical decision-making.

Synthetic information should be used for public benchmarking unless appropriate ethical, privacy, legal, security, and governance controls have been established.