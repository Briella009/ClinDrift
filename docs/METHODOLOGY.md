# ClinDrift Methodology

## Experimental Methodology for Evaluating Clinically Significant Information Drift in AI-Transformed Health Records

**Project:** ClinDrift  
**Version:** v0.1  
**Status:** Research Prototype  
**Repository:** https://github.com/Briella009/ClinDrift

---

## 1. Purpose

This document defines the experimental methodology for evaluating ClinDrift.

ClinDrift is an open-source research prototype designed to detect selected forms of clinically significant information drift between a source clinical record and an AI-transformed version of that record.

The methodology is designed to answer a central question:

> Can a deterministic, evidence-preserving verification layer reliably identify clinically significant changes introduced when health information is transformed by an AI system?

The methodology emphasises reproducibility, controlled experimentation, transparent ground truth, evidence traceability, and explicit separation between technical detection performance and clinical validation.

ClinDrift v0.1 is not clinically validated. The experiments described here are intended to evaluate the behaviour of the research prototype under controlled conditions.

---

## 2. Study Design

The initial ClinDrift evaluation uses a controlled experimental design based on synthetic clinical records and known mutations.

Each experiment begins with a source record containing predefined clinical facts.

A transformed version of that record is then produced.

The transformed record may either:

1. preserve the relevant clinical information; or
2. contain one or more deliberately introduced mutations.

Because the mutation is known in advance, the expected result can be defined before ClinDrift analyses the record.

This creates a ground-truth comparison between:

`Expected Drift`

and

`Detected Drift`

The general experimental pipeline is:

`Synthetic Source Record`

↓

`Controlled Transformation or Mutation`

↓

`Ground-Truth Label`

↓

`ClinDrift Analysis`

↓

`Detected Findings`

↓

`Evidence + Severity + Integrity Score`

↓

`Comparison With Ground Truth`

↓

`Performance Metrics`

---

## 3. Experimental Unit

The primary experimental unit is a source-transformation pair.

Each pair contains:

- a source clinical record;
- a transformed version of the record;
- one or more expected clinical facts;
- a ground-truth drift label;
- the expected drift category where applicable.

A simplified experimental pair may be represented as:

### Source

`The patient was prescribed 5 mg of Drug A once daily for 7 days.`

### Transformed

`The patient was prescribed 50 mg of Drug A once daily for 7 days.`

### Ground Truth

`Dose drift`

### Expected Behaviour

ClinDrift should identify the difference between `5 mg` and `50 mg` and produce an evidence-supported finding.

---

## 4. Data Strategy

The initial evaluation should use synthetic clinical information.

Synthetic records are preferred during prototype development because they:

- avoid exposing real patient information;
- allow exact ground truth to be defined;
- permit deliberate manipulation of clinical facts;
- support reproducible experiments;
- simplify public release of evaluation examples;
- reduce privacy and ethical risks during early-stage development.

No real patient information is required for the initial ClinDrift evaluation.

Real clinical data should only be considered in future studies after appropriate ethical, privacy, legal, governance, and security requirements have been addressed.

---

## 5. Synthetic Record Construction

Synthetic source records should contain clinically relevant concepts supported by the current ClinDrift implementation.

Initial concepts include:

- medication dosage;
- treatment duration;
- clinical measurements;
- allergy information;
- contraindication-related information where supported.

Records should vary in wording and structure while retaining clearly defined ground-truth facts.

Example:

### Record A

`The patient should take 10 mg of Drug A daily for five days.`

### Record B

`Drug A was prescribed at a dose of 10 mg once per day. Treatment duration: 5 days.`

These records express similar structured facts using different language.

Such variation helps test whether ClinDrift responds to clinical information rather than superficial sentence structure.

---

## 6. Mutation Framework

ClinDrift includes controlled mutation logic for creating known differences in clinical information.

A mutation is a deliberate modification of a source clinical fact.

The mutation framework provides an experimental mechanism for determining whether the detection engine identifies the intended change.

The initial mutation taxonomy includes:

1. dose mutation;
2. duration mutation;
3. measurement mutation;
4. allergy contradiction;
5. preserved-information control.

Future versions may expand this taxonomy.

---

## 7. Dose Mutation

A dose mutation changes the numerical medication dose while preserving surrounding information where possible.

Example:

### Source

`5 mg`

### Mutated

`50 mg`

Ground-truth label:

`DOSE_DRIFT`

The experiment succeeds when ClinDrift correctly identifies the dose difference.

Potential future variations should include:

- small numerical changes;
- large numerical changes;
- decimal changes;
- unit changes;
- equivalent unit conversions;
- frequency changes.

Equivalent unit conversions should eventually be evaluated separately because a numerical difference does not necessarily imply a clinical difference.

---

## 8. Duration Mutation

A duration mutation modifies the stated treatment duration.

Example:

### Source

`Take for 7 days.`

### Mutated

`Take for 14 days.`

Ground-truth label:

`DURATION_DRIFT`

The surrounding medication and dose should remain unchanged where possible so that the experiment isolates duration as the manipulated variable.

---

## 9. Measurement Mutation

A measurement mutation changes a supported clinical measurement.

Conceptually:

### Source

`Measurement = X`

### Mutated

`Measurement = Y`

Ground-truth label:

`MEASUREMENT_DRIFT`

Measurement experiments should preserve the associated measurement type and unit unless unit conversion itself is being tested.

Future experiments should distinguish:

- true value changes;
- equivalent unit conversions;
- rounding differences;
- formatting differences;
- clinically meaningful threshold crossings.

---

## 10. Allergy Contradiction

An allergy contradiction introduces transformed information that conflicts with the allergy status represented in the source.

Example:

### Source

`The patient has an allergy to Drug A.`

### Transformed

`No known allergy to Drug A.`

Ground-truth label:

`ALLERGY_CONTRADICTION`

Allergy-related experiments are particularly important because negation and omission can substantially alter meaning while requiring only a small textual change.

---

## 11. Preserved-Information Control

ClinDrift must be evaluated not only on its ability to detect mutations but also on its ability to avoid flagging information that has been preserved.

A preserved-information case acts as a negative control.

Example:

### Source

`The patient's temperature was 37.2°C.`

### Transformed

`A temperature of 37.2°C was recorded for the patient.`

Ground-truth label:

`NO_DRIFT`

Expected result:

ClinDrift should not report a measurement drift merely because the sentence has been rephrased.

Negative controls are essential for measuring false positives.

---

## 12. Single-Mutation Experiments

The first experimental phase should evaluate one mutation at a time.

This isolates the behaviour of each detection rule.

For each supported drift category:

1. create a valid source record;
2. preserve all unrelated clinical facts;
3. mutate exactly one target concept;
4. record the expected ground-truth label;
5. run ClinDrift;
6. record the detected result;
7. compare detected and expected outcomes.

Single-mutation experiments provide the clearest initial assessment of rule correctness.

---

## 13. Multi-Mutation Experiments

After single-mutation performance is established, the evaluation should introduce multiple changes within the same transformed record.

Example:

### Source

`5 mg for 7 days with a documented Drug A allergy.`

### Transformed

`50 mg for 14 days with no documented Drug A allergy.`

Possible ground truth:

- dose drift;
- duration drift;
- allergy contradiction.

Multi-mutation experiments evaluate whether one detected issue interferes with detection of another.

They also allow integrity-score behaviour to be examined as the number and severity of findings increase.

---

## 14. Transformation Conditions

The evaluation should distinguish between mutation and linguistic transformation.

A future benchmark should contain several transformation conditions.

### Condition A: Exact Preservation

The transformed record is identical to the source.

Expected result:

`NO_DRIFT`

### Condition B: Meaning-Preserving Rephrasing

The wording changes but supported clinical facts remain unchanged.

Expected result:

`NO_DRIFT`

### Condition C: Single Clinical Mutation

One supported clinical fact changes.

Expected result:

The corresponding drift category should be detected.

### Condition D: Multiple Clinical Mutations

Several supported facts change.

Expected result:

Each supported mutation should be identified independently where possible.

### Condition E: Unsupported Transformation

The transformation contains a change outside the current ClinDrift taxonomy.

This condition is useful for documenting the boundaries of the prototype.

ClinDrift should not be assumed to detect unsupported error categories.

---

## 15. Ground Truth

Ground truth must be established before running the detection engine.

For synthetic mutation experiments, ground truth is determined directly from the controlled mutation operation.

Each test case should record:

- case identifier;
- source facts;
- transformed facts;
- mutation applied;
- expected drift category;
- expected affected value;
- expected non-affected values.

Example:

`case_id: CD-D001`

`mutation: dose`

`source_value: 5 mg`

`transformed_value: 50 mg`

`expected_label: DOSE_DRIFT`

This prevents evaluation labels from being changed after observing ClinDrift's output.

---

## 16. Case Identification

Each experimental case should receive a unique identifier.

A recommended naming convention is:

`CD-[CATEGORY]-[NUMBER]`

Examples:

`CD-D001` = Dose experiment

`CD-T001` = Duration experiment

`CD-M001` = Measurement experiment

`CD-A001` = Allergy experiment

`CD-N001` = No-drift negative control

`CD-X001` = Multi-mutation experiment

Unique identifiers improve traceability between:

- source data;
- ground truth;
- ClinDrift output;
- test results;
- analysis;
- research reports.

---

## 17. ClinDrift Processing Procedure

For each experimental pair, the following procedure should be applied consistently.

### Step 1

Load the source record.

### Step 2

Load the transformed record.

### Step 3

Extract supported clinical concepts from the source.

### Step 4

Extract the corresponding concepts from the transformed record.

### Step 5

Run the drift-detection rules.

### Step 6

Record all detected findings.

### Step 7

Record the evidence associated with each finding.

### Step 8

Record severity classifications.

### Step 9

Calculate the integrity score.

### Step 10

Record human-review status where applicable.

### Step 11

Compare the detected findings with the predefined ground truth.

### Step 12

Store the result for aggregate evaluation.

---

## 18. Outcome Classification

Each expected drift event can be classified using standard detection outcomes.

### True Positive

A mutation exists and ClinDrift correctly detects it.

### False Positive

No relevant mutation exists but ClinDrift reports one.

### True Negative

No relevant mutation exists and ClinDrift correctly reports no corresponding drift.

### False Negative

A relevant mutation exists but ClinDrift fails to detect it.

These classifications form the basis of quantitative evaluation.

---

## 19. Precision

Precision measures how many reported findings are correct.

`Precision = TP / (TP + FP)`

where:

`TP = True Positives`

`FP = False Positives`

High precision indicates that ClinDrift produces relatively few incorrect alerts.

This is important because excessive false alerts may reduce reviewer trust and increase review burden.

---

## 20. Recall

Recall measures how many known mutations are detected.

`Recall = TP / (TP + FN)`

where:

`FN = False Negatives`

High recall is particularly important in safety-oriented verification because missed clinically relevant changes may remain unnoticed.

Precision and recall should therefore be considered together.

---

## 21. F1 Score

The F1 score provides a combined measure of precision and recall.

`F1 = 2 × (Precision × Recall) / (Precision + Recall)`

F1 should be reported overall and, where sufficient cases exist, separately for each drift category.

---

## 22. False Positive Rate

Negative-control cases should be used to evaluate unnecessary findings.

A false positive occurs when ClinDrift reports a supported drift category even though the relevant clinical fact has been preserved.

The false positive rate can be calculated as:

`FPR = FP / (FP + TN)`

where:

`TN = True Negatives`

Meaning-preserving transformations are particularly important for this evaluation.

---

## 23. Category-Level Performance

Aggregate performance alone may conceal weaknesses in individual rules.

Results should therefore be reported separately for:

- dose drift;
- duration drift;
- measurement drift;
- allergy contradiction;
- preserved-information cases.

For each supported category, report where possible:

- number of cases;
- true positives;
- false positives;
- false negatives;
- true negatives;
- precision;
- recall;
- F1 score.

---

## 24. Evidence Evaluation

Detection alone is not sufficient for ClinDrift's intended research contribution.

The system also aims to preserve evidence.

Each detected finding should therefore be evaluated for evidence correctness.

Questions include:

1. Does the finding identify the correct clinical concept?
2. Does it contain the correct source value?
3. Does it contain the correct transformed value?
4. Can the reviewer determine why the finding was generated?
5. Is the evidence associated with the correct experimental case?

A finding that correctly predicts a drift category but attaches incorrect evidence should be recorded as an evidence failure.

---

## 25. Severity Evaluation

Severity should initially be evaluated as an internal consistency mechanism.

For identical mutation types under identical conditions, severity assignment should be deterministic.

The evaluation should verify that:

- the same rule produces the same severity when inputs are equivalent;
- severity contributes consistently to integrity scoring;
- severity labels are preserved in exported results.

Clinical validity of severity levels is outside the scope of the initial software evaluation.

Future studies should compare severity assignments with independent expert judgement.

---

## 26. Integrity Score Evaluation

The ClinDrift integrity score should be evaluated for deterministic and monotonic behaviour where appropriate.

The evaluation should examine whether:

- a preserved record produces a high integrity score;
- introduction of a supported mutation reduces integrity where intended;
- more severe findings have an appropriately greater effect where defined;
- multiple findings behave consistently;
- identical inputs produce identical scores.

The score should not be interpreted as a probability of clinical harm.

The objective is to evaluate internal scoring behaviour, not medical risk prediction.

---

## 27. Human Review Evaluation

Where the prototype allows human review, the following information should be recorded:

- original automated finding;
- evidence presented;
- reviewer decision;
- review status;
- reviewer notes where applicable.

Possible review outcomes may include:

- confirmed;
- rejected;
- uncertain;
- requires additional context.

The automated finding should remain distinguishable from the human decision.

This separation is important for auditability.

---

## 28. Reproducibility

Every formal experimental run should record sufficient information to allow the experiment to be reproduced.

At minimum:

- ClinDrift version;
- Git commit identifier;
- Python version;
- dependency versions;
- operating environment where relevant;
- dataset version;
- mutation configuration;
- case identifiers;
- expected labels;
- test command;
- evaluation date.

The current automated tests can be executed with:

`python -m pytest -v`

All formal research results should be linked to a specific repository state rather than only a project name.

---

## 29. Automated Unit Testing

Automated tests provide the first level of verification.

ClinDrift v0.1 currently includes tests covering core behaviours including:

- dose drift detection;
- preserved measurement behaviour;
- allergy contradiction detection;
- duration drift detection.

The test suite should be run:

- before a release;
- after modifications to detection logic;
- after modifications to extraction logic;
- after modifications to scoring;
- before reporting experimental results.

A failing test should be investigated before the affected version is used for formal evaluation.

---

## 30. Regression Testing

As ClinDrift evolves, previously successful test cases should remain part of the test suite.

This creates a regression-testing mechanism.

When a new feature is introduced, the project should verify that previously supported behaviours still work.

For example, adding a new medication-frequency detector should not cause previously passing duration-drift tests to fail.

Regression testing is particularly important when multiple extraction and detection rules interact.

---

## 31. Benchmark Dataset Development

The initial sample cases are sufficient for software verification but not for strong empirical claims.

A larger synthetic benchmark should therefore be developed.

A future benchmark should contain:

- multiple cases per drift category;
- multiple linguistic formulations;
- multiple numerical values;
- negative controls;
- meaning-preserving paraphrases;
- single mutations;
- multiple simultaneous mutations;
- edge cases;
- deliberately difficult cases.

The benchmark should be versioned.

Example:

`ClinDrift Synthetic Benchmark v0.1`

Future changes to the benchmark should result in new versions so that results remain comparable.

---

## 32. Recommended Initial Benchmark Size

The first structured evaluation should aim for enough cases to expose rule failures rather than relying on only one example per category.

A practical initial target may include:

- 25 dose cases;
- 25 duration cases;
- 25 measurement cases;
- 25 allergy cases;
- 50 no-drift controls;
- 25 multi-mutation cases.

This would produce approximately 175 experimental record pairs.

This number is a development target rather than a statistical claim.

A formal publication should justify the final dataset size based on the intended analysis.

---

## 33. Baseline Methods

ClinDrift should eventually be compared with baseline approaches.

Potential baselines include:

### Exact String Comparison

Tests whether the source and transformed text are identical.

This baseline is expected to be highly sensitive to harmless rephrasing.

### Token Similarity

Measures lexical overlap between records.

### Semantic Similarity

Uses sentence-level or document-level representations to estimate semantic similarity.

### Embedding Similarity

Represents records as vectors and compares their distance.

### LLM-Based Verification

Asks a generative model to identify whether clinically relevant information changed.

### Structured Field Comparison

Where structured clinical fields are available, values can be compared directly.

The purpose of baseline comparison is not necessarily to demonstrate that ClinDrift outperforms every method.

The evaluation should investigate differences in:

- detection performance;
- interpretability;
- reproducibility;
- evidence traceability;
- computational complexity;
- failure modes.

---

## 34. AI Transformation Evaluation

A later experimental phase should test ClinDrift against actual AI-generated transformations.

Possible tasks include:

- clinical summarisation;
- rewriting;
- translation;
- discharge-summary simplification;
- structured-to-text generation;
- text-to-structured extraction;
- clinical note condensation.

The workflow would become:

`Source Record`

↓

`AI System`

↓

`AI-Transformed Record`

↓

`ClinDrift`

↓

`Verification Result`

Unlike synthetic mutations, AI-generated errors may not have predefined ground truth.

Such experiments would therefore require independent annotation.

---

## 35. Human Annotation for Future AI Experiments

For experiments involving uncontrolled AI transformations, at least two independent reviewers should ideally evaluate whether clinically significant information changed.

Where reviewers disagree, an adjudication procedure should be defined.

The annotation protocol should specify:

- supported drift categories;
- definitions;
- examples;
- exclusion criteria;
- disagreement handling;
- uncertainty labels.

Inter-rater agreement may also be measured.

This phase should only be introduced after the controlled synthetic evaluation is sufficiently mature.

---

## 36. Error Analysis

Every false positive and false negative should be examined qualitatively.

For each error, record:

- case identifier;
- expected result;
- detected result;
- affected rule;
- probable cause;
- whether extraction failed;
- whether comparison failed;
- whether the case exposed an unsupported condition;
- proposed corrective action.

Error analysis is essential because aggregate metrics alone cannot explain why the system fails.

---

## 37. Failure Taxonomy

Observed failures should be classified.

Potential categories include:

### Extraction Failure

The relevant clinical concept was not extracted correctly.

### Matching Failure

The correct concepts were extracted but paired incorrectly.

### Detection Failure

The relevant difference existed but the rule failed to recognise it.

### False Equivalence

ClinDrift treated two clinically different values as equivalent.

### False Difference

ClinDrift treated clinically equivalent information as different.

### Unsupported Drift

The transformation contained a clinically relevant change outside the implemented taxonomy.

### Evidence Failure

The finding was correct but the supporting evidence was incomplete or incorrect.

### Scoring Failure

Findings were correct but the integrity score behaved unexpectedly.

This taxonomy can guide future development.

---

## 38. Ablation Studies

Future versions may use ablation studies to determine the contribution of individual components.

For example, evaluate performance:

- with evidence extraction enabled;
- without evidence extraction;
- with severity weighting;
- without severity weighting;
- with individual detection rules removed.

Ablation experiments can help establish which components materially contribute to the system's behaviour.

---

## 39. Robustness Testing

Future robustness testing should deliberately vary record formatting.

Potential variations include:

- uppercase and lowercase differences;
- punctuation changes;
- whitespace changes;
- sentence order changes;
- abbreviations;
- alternative medication formatting;
- decimal formatting;
- different date formats;
- different duration expressions;
- unit formatting.

Clinically equivalent formatting changes should not generate inappropriate drift findings.

---

## 40. Boundary Testing

Boundary cases should be created deliberately.

Examples include:

- `5 mg` versus `5.0 mg`;
- `500 mg` versus `0.5 g`;
- `7 days` versus `1 week`;
- measurement rounding;
- explicit allergy versus allergy negation;
- missing values;
- duplicated clinical facts.

Some of these cases may not be supported by v0.1.

Unsupported cases should be documented rather than silently interpreted as successful behaviour.

---

## 41. Determinism Testing

Because ClinDrift v0.1 is designed around deterministic verification, identical inputs should produce identical outputs.

A determinism experiment should:

1. select a fixed source-transformation pair;
2. execute ClinDrift repeatedly;
3. compare findings;
4. compare severity;
5. compare evidence;
6. compare integrity scores.

Unexpected output variation should be treated as a reproducibility issue.

---

## 42. Performance Testing

Runtime performance is not the primary objective of v0.1, but basic performance measurements may still be useful.

Future experiments may record:

- processing time per record pair;
- processing time by record length;
- memory usage;
- performance across batch sizes.

These measurements may become more important if ClinDrift is extended to larger clinical datasets.

---

## 43. Privacy Evaluation

The public research workflow should verify that no identifiable patient information is required.

Repository checks should confirm that:

- synthetic data are used in public examples;
- private-data directories remain excluded from version control;
- uploaded patient records are not committed;
- generated reports do not inadvertently expose sensitive data.

Privacy testing should become more formal if the project later processes real clinical information.

---

## 44. Security Evaluation

Future security evaluation should consider threats to the verification system itself.

Examples include:

- maliciously crafted records;
- parser manipulation;
- oversized inputs;
- dependency vulnerabilities;
- unsafe file uploads;
- injection attacks;
- tampering with evidence;
- tampering with integrity scores;
- unauthorised modification of review outcomes.

If ClinDrift later integrates external AI APIs, additional risks should include:

- data leakage;
- prompt injection;
- third-party retention;
- model-output manipulation;
- API credential exposure.

---

## 45. Statistical Reporting

Formal evaluation results should report raw counts in addition to summary metrics.

For example:

| Metric | Result |
|---|---:|
| Total cases | N |
| True positives | TP |
| False positives | FP |
| True negatives | TN |
| False negatives | FN |
| Precision | Value |
| Recall | Value |
| F1 | Value |
| False positive rate | Value |

Category-specific tables should also be included.

Where appropriate, confidence intervals should be reported in later larger evaluations.

---

## 46. Result Interpretation

Passing unit tests should not be interpreted as evidence that ClinDrift is clinically safe.

Likewise, strong performance on synthetic mutations would demonstrate performance only within the evaluated conditions.

Results should be interpreted according to the evidence available.

Appropriate claim:

> ClinDrift detected the evaluated synthetic dose mutations with X performance under the specified experimental conditions.

Inappropriate claim:

> ClinDrift prevents medication errors in hospitals.

The methodology intentionally limits conclusions to what the experiments actually establish.

---

## 47. Threats to Internal Validity

Internal validity may be affected by:

- incorrect ground-truth labels;
- implementation bugs;
- mutation-generation errors;
- overlap between training/development examples and evaluation cases;
- inconsistent experimental configuration;
- evaluation-code errors.

Mitigation strategies include:

- automated tests;
- fixed ground truth;
- version control;
- manual inspection of sample mutations;
- reproducible scripts;
- independent verification where possible.

---

## 48. Threats to External Validity

Results from synthetic records may not generalise directly to:

- real electronic health records;
- different healthcare systems;
- different clinical specialties;
- long clinical narratives;
- multilingual records;
- noisy clinical notes;
- uncommon medications;
- different AI transformation systems.

External validity should therefore be investigated separately in future work.

---

## 49. Threats to Construct Validity

Clinically significant information drift is broader than the current implemented categories.

Dose, duration, measurement, and allergy changes represent only part of the problem.

Other clinically meaningful errors may include:

- diagnosis omission;
- negation reversal;
- temporal changes;
- medication-frequency changes;
- procedure changes;
- patient identity confusion;
- causal distortion;
- uncertainty removal.

The current evaluation therefore measures performance on selected drift constructs rather than all forms of clinical information integrity.

---

## 50. Ethical Considerations

The initial methodology intentionally uses synthetic data to reduce risk.

The prototype should not be tested prospectively on patient care.

Any future study involving real patient records, clinicians, healthcare institutions, or clinical workflows should determine whether ethical review or institutional approval is required.

Research involving identifiable health information should also address applicable privacy and data-protection requirements.

---

## 51. Clinical Safety Boundary

ClinDrift outputs must remain research outputs.

The experimental workflow must not instruct clinicians to:

- prescribe medication;
- discontinue medication;
- change dosage;
- diagnose a condition;
- alter treatment;
- make an emergency-care decision.

ClinDrift detects information differences.

It does not determine appropriate medical treatment.

---

## 52. Experimental Logging

Each formal experiment should generate or retain a structured log containing:

- experiment identifier;
- timestamp;
- ClinDrift version;
- commit hash;
- case identifier;
- mutation type;
- source value;
- transformed value;
- expected result;
- detected result;
- severity;
- integrity score;
- evidence;
- review outcome where applicable.

Structured logs will support later statistical analysis.

---

## 53. Recommended Experiment Naming

A consistent naming structure should be used.

Example:

`EXP-CD-v0.1-001`

A complete experiment might therefore contain:

`Experiment: EXP-CD-v0.1-001`

`Case: CD-D001`

`Version: v0.1`

`Mutation: DOSE_DRIFT`

This provides traceability from published results back to individual cases.

---

## 54. Version Control

Every experimental result intended for publication should reference the exact Git commit used.

For example:

`ClinDrift version: v0.1`

`Git commit: <commit-hash>`

This is more reliable than referencing only the repository's current `main` branch because the code may change after an experiment is completed.

---

## 55. Release Strategy

Formal experimental milestones should be associated with tagged releases where practical.

Examples:

`v0.1.0` — Initial research prototype

`v0.2.0` — Expanded synthetic benchmark

`v0.3.0` — Baseline comparison

`v0.4.0` — AI-transformation evaluation

Release notes should describe:

- new functionality;
- changed detection rules;
- dataset changes;
- known limitations;
- test status.

---

## 56. Open Science

Where legally and ethically possible, research based on ClinDrift should make available:

- source code;
- synthetic benchmark data;
- mutation definitions;
- evaluation scripts;
- metric calculations;
- experiment configuration;
- software version;
- documentation.

This supports independent replication.

Real patient data should not be released merely for reproducibility.

Synthetic or appropriately governed alternatives should be preferred.

---

## 57. Proposed Evaluation Phases

The ClinDrift research programme can be divided into five phases.

### Phase 1: Software Verification

Confirm that implemented rules behave as expected.

Includes:

- unit testing;
- regression testing;
- deterministic behaviour testing.

### Phase 2: Controlled Synthetic Benchmark

Evaluate ClinDrift against a larger set of known mutations.

Includes:

- single mutations;
- negative controls;
- multi-mutation cases;
- precision;
- recall;
- F1;
- false positive analysis.

### Phase 3: Baseline Comparison

Compare ClinDrift against general-purpose comparison approaches.

### Phase 4: Real AI Transformations

Generate transformations using actual AI systems and assess information preservation.

### Phase 5: Expert Evaluation

Where feasible and ethically appropriate, involve qualified domain experts in evaluating findings, evidence, and clinical relevance.

Each phase should be completed and documented before stronger claims are made.

---

## 58. Minimum Criteria for v0.1 Evaluation

Before considering the v0.1 experimental foundation complete, the following should be available:

- functioning ClinDrift prototype;
- documented drift taxonomy;
- synthetic source cases;
- controlled mutation mechanisms;
- automated tests;
- predefined ground truth;
- evidence traceability;
- integrity scoring;
- documented methodology;
- reproducible execution instructions.

These criteria establish readiness for a larger benchmark evaluation.

They do not establish clinical readiness.

---

## 59. Current Test Baseline

At the current prototype stage, the automated test suite contains four core tests covering:

1. dose drift detection;
2. preserved measurement not being incorrectly flagged;
3. allergy contradiction detection;
4. duration drift detection.

The current suite passes all four implemented tests.

This baseline should be preserved as the project expands.

Any future change that causes one of these tests to fail should be investigated before release.

---

## 60. Next Experimental Action

The immediate next experimental step after documenting this methodology is to construct the first versioned ClinDrift synthetic benchmark.

The benchmark should contain enough cases to evaluate both successful detection and failure behaviour.

The workflow will then progress from:

`Does the code work on four predefined tests?`

to:

`How accurately does ClinDrift perform across a systematically constructed evaluation dataset?`

That transition is necessary before the prototype can support meaningful empirical research claims.

---

## 61. Methodology Summary

ClinDrift v0.1 uses a controlled, evidence-oriented evaluation methodology.

The core methodological principles are:

1. use synthetic data during initial evaluation;
2. define ground truth before detection;
3. introduce controlled clinical mutations;
4. include meaning-preserving negative controls;
5. evaluate each drift category independently;
6. introduce multi-mutation cases after single-rule verification;
7. record evidence and severity, not only detection labels;
8. evaluate integrity-score behaviour;
9. report false positives and false negatives;
10. preserve exact software and dataset versions;
11. analyse failures qualitatively;
12. compare against appropriate baselines in later experiments;
13. keep automated findings separate from human clinical judgement;
14. restrict claims to the conditions actually evaluated.

This methodology provides the foundation for turning ClinDrift from a functioning prototype into a reproducible research artefact.

---

## Disclaimer

ClinDrift is an experimental research prototype.

The methodology described here is intended for research, software evaluation, and controlled experimentation.

ClinDrift has not been clinically validated and must not be used independently for diagnosis, treatment, medication management, patient monitoring, or other clinical decision-making.

Synthetic data should be used for public experiments unless appropriate ethical, privacy, security, legal, and governance controls have been established.