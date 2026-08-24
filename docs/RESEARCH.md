# ClinDrift Research Documentation

## Research Prototype for Detecting Clinically Significant Information Drift in AI-Transformed Health Records

**Project:** ClinDrift  
**Version:** v0.1  
**Status:** Research Prototype  
**Repository:** https://github.com/Briella009/ClinDrift

---

## 1. Research Overview

ClinDrift is an open-source research prototype designed to investigate a specific safety problem in AI-enabled digital health systems: clinically significant information can change, disappear, or become contradictory when health records are transformed by artificial intelligence systems.

AI systems are increasingly capable of summarising, restructuring, translating, extracting, and generating clinical information. These capabilities may improve efficiency, but they also introduce a critical question:

> How can we verify that clinically important information remains faithful to the source record after an AI system transforms it?

ClinDrift explores this problem through deterministic comparison between an original clinical record and an AI-transformed version of that record.

Rather than evaluating whether generated clinical text sounds fluent or plausible, ClinDrift focuses on whether safety-relevant clinical facts have been preserved.

The prototype currently concentrates on structured clinical concepts including medication dosage, measurement values, allergies, contraindications, and treatment duration.

---

## 2. Research Problem

Generative AI and other automated language-processing systems can transform clinical information in ways that appear reasonable while still introducing clinically meaningful errors.

Examples include:

- changing a medication dosage;
- changing the frequency of medication administration;
- omitting an allergy;
- introducing an allergy contradiction;
- altering a laboratory or physiological measurement;
- changing the duration of treatment;
- removing clinically important qualifiers;
- producing a transformed record that appears fluent but is not faithful to the original.

These changes may be difficult to detect through ordinary text comparison because the transformed record may use different wording while preserving some facts and modifying others.

In healthcare, however, small changes can have disproportionate consequences.

A transformation from `5 mg` to `50 mg`, for example, is linguistically minor but potentially clinically significant.

ClinDrift therefore treats clinical information preservation as an integrity problem rather than simply a text-similarity problem.

---

## 3. Research Question

The primary research question guiding ClinDrift is:

> Can a deterministic, evidence-preserving verification layer identify clinically significant information drift between source health records and AI-transformed versions of those records?

Supporting questions include:

1. Which categories of clinical information drift can be detected reliably using deterministic rules?
2. Can detected drift be accompanied by sufficient evidence to allow a human reviewer to verify the finding?
3. Can multiple detected changes be converted into a transparent clinical integrity score?
4. Can the system distinguish meaningful clinical changes from information that has been preserved despite linguistic transformation?
5. Can human review be incorporated without allowing the system to make autonomous clinical decisions?
6. Can synthetic mutation testing provide a reproducible method for evaluating clinical information-preservation mechanisms?

---

## 4. Research Objectives

ClinDrift has six primary research objectives.

### Objective 1: Detect Clinical Information Drift

Develop deterministic mechanisms for identifying changes between source and transformed clinical information.

Initial drift categories include:

- medication dose drift;
- treatment-duration drift;
- measurement drift;
- allergy contradictions;
- other structured clinical inconsistencies supported by the prototype.

### Objective 2: Preserve Evidence

Every detected issue should be traceable to evidence from the records being compared.

The prototype is intended to show what changed rather than returning an unexplained risk prediction.

### Objective 3: Estimate Information Integrity

ClinDrift uses detected findings and their severity to produce an interpretable integrity score.

The score is intended as a research signal for information preservation.

It is not a probability of patient harm and is not a clinical diagnosis.

### Objective 4: Support Human Review

ClinDrift is designed as a human-in-the-loop verification mechanism.

The system may identify potential drift, but final interpretation remains with a human reviewer.

### Objective 5: Support Reproducible Testing

The project includes automated tests and synthetic mutations so that expected behaviours can be evaluated consistently.

### Objective 6: Provide Auditable Outputs

ClinDrift aims to produce reviewable outputs that can support research, experimentation, governance analysis, and future evaluation.

---

## 5. Research Hypothesis

The working hypothesis is:

> Clinically significant information drift can be detected using transparent deterministic comparison rules while preserving evidence sufficient for independent human review.

A secondary hypothesis is:

> An integrity-oriented evaluation approach can provide more clinically meaningful signals than relying exclusively on general linguistic similarity between source and AI-transformed health records.

These hypotheses remain subject to empirical evaluation.

ClinDrift v0.1 should therefore be treated as an experimental prototype rather than a validated clinical system.

---

## 6. Concept of Clinical Information Drift

For ClinDrift, clinical information drift refers to a clinically relevant difference introduced between a source record and a transformed record.

Let:

- **S** represent the source clinical record;
- **T** represent the transformed record;
- **E(S)** represent clinically relevant information extracted from the source;
- **E(T)** represent clinically relevant information extracted from the transformed record.

ClinDrift evaluates differences between:

`E(S)` and `E(T)`

A difference is considered potentially significant when it affects a clinical concept covered by the prototype's rule set.

This definition intentionally separates clinical information preservation from general textual similarity.

Two passages may use substantially different wording while preserving the same clinical meaning.

Conversely, two passages may be nearly identical while containing one dangerous numerical or categorical change.

---

## 7. Why Text Similarity Alone Is Insufficient

Consider the following simplified example.

### Source

`The patient should receive 5 mg of the medication for 7 days.`

### Transformed

`The patient should receive 50 mg of the medication for 7 days.`

Most of the sentence remains identical.

A generic similarity measure could therefore assign a very high similarity score.

Clinically, however, the dosage has changed by a factor of ten.

ClinDrift is designed around this distinction.

The prototype asks:

> Which clinical facts changed?

rather than only:

> How similar are these two pieces of text?

---

## 8. Current Drift Categories

ClinDrift v0.1 focuses on a deliberately limited set of detectable changes.

### 8.1 Dose Drift

A medication dose in the transformed record differs from the corresponding dose in the source record.

Example:

`5 mg → 50 mg`

### 8.2 Measurement Drift

A structured clinical measurement changes between the source and transformed records.

The exact interpretation depends on the measurement represented in the test case.

### 8.3 Allergy Contradiction

The transformed record introduces information that conflicts with allergy information contained in the source record.

Allergy-related changes are treated cautiously because omission or contradiction may have direct safety implications.

### 8.4 Duration Drift

The duration of treatment changes.

Example:

`7 days → 14 days`

### 8.5 Preserved Information

Not every textual transformation should generate an alert.

If a clinically relevant measurement or fact remains equivalent after transformation, the system should avoid flagging it simply because surrounding language has changed.

This behaviour is important for controlling unnecessary findings.

---

## 9. Detection Philosophy

ClinDrift currently uses deterministic rules rather than an opaque predictive model.

This is intentional.

For an early-stage safety research prototype, deterministic logic provides several advantages:

- findings can be reproduced;
- rules can be inspected;
- expected behaviour can be unit tested;
- evidence can be attached directly to findings;
- errors in the verification logic can be investigated;
- researchers can understand why a finding was produced.

The current design does not assume that deterministic methods will solve every clinical-information-preservation problem.

Instead, the prototype establishes an auditable baseline against which more advanced approaches could later be evaluated.

---

## 10. Evidence Traceability

A core principle of ClinDrift is:

> A detected change should not be separated from the evidence used to detect it.

Where supported by the implementation, findings should make it possible to determine:

- the affected clinical concept;
- the source value;
- the transformed value;
- the type of drift detected;
- the assigned severity;
- the evidence associated with the finding.

This design supports human verification and reduces dependence on unexplained automated conclusions.

---

## 11. Severity

Detected findings may be assigned severity levels based on the type and potential significance of the information change.

Severity is used to prioritise findings and contribute to integrity scoring.

The severity mechanism is a research heuristic.

It must not be interpreted as a validated estimate of clinical harm.

Future research should evaluate whether severity assignments correspond appropriately with expert clinical judgement.

---

## 12. Clinical Integrity Score

ClinDrift includes an integrity scoring mechanism intended to summarise the degree to which safety-relevant information appears to have been preserved.

Conceptually:

`High integrity = little or no detected clinically significant drift`

`Lower integrity = more and/or more severe detected drift`

The score is designed to remain interpretable.

It is not intended to represent:

- probability of patient injury;
- probability that an AI system is unsafe;
- diagnostic confidence;
- medical risk prediction;
- regulatory approval;
- clinical validation.

The integrity score is an experimental research metric.

---

## 13. Human Review

ClinDrift is not intended to replace clinicians.

Its role is closer to a verification layer.

A possible workflow is:

`Source Record`

↓

`AI Transformation`

↓

`ClinDrift Verification`

↓

`Detected Drift + Evidence + Integrity Score`

↓

`Human Review`

↓

`Review Status / Decision`

The human-review layer is important because a detected difference may require context that deterministic software cannot infer safely.

A reviewer may therefore need to determine whether a detected difference is:

- clinically meaningful;
- acceptable;
- expected;
- caused by source-record ambiguity;
- caused by transformation error;
- caused by a limitation in ClinDrift's extraction or detection logic.

---

## 14. Synthetic Mutation Testing

Evaluating clinical drift detection requires known changes.

ClinDrift therefore includes mutation logic that can deliberately alter selected clinical information.

Synthetic mutations provide controlled examples where the expected difference is known in advance.

Examples may include:

- modifying a dosage;
- changing treatment duration;
- changing a measurement;
- introducing an allergy contradiction.

This creates a reproducible evaluation structure:

`Original Record`

↓

`Controlled Mutation`

↓

`Known Expected Drift`

↓

`ClinDrift Detection`

↓

`Compare Expected vs Detected Result`

This approach allows the detection engine to be tested without requiring real patient records.

---

## 15. Automated Testing

ClinDrift v0.1 includes automated unit tests for core behaviours.

The current test suite evaluates behaviours including:

- detection of dose drift;
- preservation of unchanged measurements without false flagging;
- detection of allergy contradiction;
- detection of duration drift.

The prototype has successfully passed its current core test suite.

At the v0.1 stage, the passing tests demonstrate that the implemented rules behave as expected for the defined test cases.

They do not establish clinical validity or generalisability.

Future versions should substantially expand the test corpus.

---

## 16. Synthetic Data and Privacy

ClinDrift is designed to support experimentation without requiring real patient information.

The repository includes synthetic/sample cases for development and testing.

Real identifiable patient information should not be committed to the public repository.

The project `.gitignore` is configured to exclude designated local data locations such as private patient data and uploaded records.

Researchers and contributors remain responsible for ensuring that protected health information, personally identifiable information, or confidential clinical records are not accidentally committed.

---

## 17. Explainability

Explainability in ClinDrift is based primarily on traceability rather than natural-language justification.

A useful finding should allow a reviewer to inspect the relationship:

`Source evidence → Extracted concept → Detected change → Severity → Integrity impact`

This is intentionally different from asking a generative model to explain its own output.

The verification mechanism should provide independently inspectable evidence wherever possible.

---

## 18. Research Architecture

The current prototype separates several responsibilities.

### Application Layer

`app.py`

Provides the user-facing prototype interface and coordinates the research workflow.

### Extraction Layer

`src/extractor.py`

Extracts relevant clinical concepts from records.

### Drift Detection Layer

`src/drift_engine.py`

Compares extracted information and identifies supported forms of clinical information drift.

### Mutation Layer

`src/mutations.py`

Creates controlled synthetic changes for testing and research evaluation.

### Scoring Layer

`src/scoring.py`

Converts detected findings into an interpretable integrity-oriented score.

### Testing Layer

`tests/`

Contains automated tests used to verify expected behaviour.

### Sample Data

`data/sample_cases.json`

Contains synthetic examples used for demonstration and testing.

---

## 19. Research Workflow

The conceptual ClinDrift workflow is:

`1. Obtain a source clinical record`

↓

`2. Obtain or generate an AI-transformed version`

↓

`3. Extract supported clinical concepts from both versions`

↓

`4. Compare the extracted information`

↓

`5. Identify supported drift categories`

↓

`6. Assign severity where applicable`

↓

`7. Preserve evidence associated with findings`

↓

`8. Calculate an integrity score`

↓

`9. Present findings for human review`

↓

`10. Record or export the review outcome`

This workflow is intended to keep automated detection separate from final clinical judgement.

---

## 20. Intended Research Use

ClinDrift may be useful for research involving:

- trustworthy AI in healthcare;
- clinical NLP safety;
- generative AI evaluation;
- health-information integrity;
- AI governance;
- human oversight of healthcare AI;
- clinical summarisation verification;
- explainable AI safety mechanisms;
- digital-health cybersecurity;
- assurance mechanisms for AI-transformed records.

The prototype may also provide a foundation for controlled experiments comparing different transformation systems.

---

## 21. Potential Experimental Design

A future ClinDrift evaluation could construct a benchmark containing source records and controlled transformations.

For each source record, researchers could generate:

1. a meaning-preserving transformation;
2. a dose mutation;
3. a duration mutation;
4. a measurement mutation;
5. an allergy contradiction;
6. combinations of multiple mutations.

ClinDrift could then be evaluated using metrics such as:

- true positives;
- false positives;
- true negatives;
- false negatives;
- precision;
- recall;
- F1 score;
- detection performance by drift category;
- integrity-score behaviour under increasing mutation severity.

Human expert review could subsequently be used to assess clinical relevance.

---

## 22. Baseline Comparison

Future research should compare ClinDrift with appropriate baselines rather than evaluating the system in isolation.

Potential baselines include:

- exact text comparison;
- token-level similarity;
- semantic similarity;
- embedding-based similarity;
- LLM-based verification;
- structured field comparison where structured source data are available.

The research question would not simply be whether ClinDrift detects errors.

A stronger question is:

> Does clinically targeted, evidence-preserving drift detection identify safety-relevant changes more reliably or more transparently than general-purpose similarity approaches?

---

## 23. Evaluation Metrics

Future empirical evaluation should report metrics appropriate to the task.

At minimum:

### Precision

Of all changes ClinDrift flags, how many represent the intended drift category?

### Recall

Of all deliberately introduced clinically relevant changes, how many does ClinDrift detect?

### F1 Score

What is the balance between precision and recall?

### False Positive Rate

How frequently does ClinDrift flag information that was actually preserved?

### Drift-Type Performance

Does performance differ between dose, duration, measurement, allergy, and other supported categories?

### Evidence Accuracy

Does the evidence attached to a finding correctly identify the information responsible for that finding?

### Integrity-Score Behaviour

Does the integrity score respond consistently as known mutations are introduced?

---

## 24. Threats to Validity

Several limitations must be considered when interpreting results from ClinDrift.

### Synthetic Data Bias

Synthetic cases may be cleaner and less ambiguous than real clinical records.

### Limited Drift Taxonomy

The current prototype covers only selected forms of clinical information drift.

### Extraction Error

A failure to extract the correct clinical concept may affect downstream drift detection.

### Rule Dependence

Deterministic rules may not generalise to every clinical writing style or transformation.

### Clinical Context

A numerical or textual change cannot always be interpreted safely without broader patient context.

### Mutation Realism

Synthetic mutations may not perfectly reproduce the errors generated by real-world AI systems.

### Lack of Clinical Validation

The current prototype has not been clinically validated.

These limitations should be reported explicitly in any publication or presentation based on the project.

---

## 25. Safety Boundaries

ClinDrift v0.1 is a research prototype.

It is not:

- a medical device;
- a diagnostic system;
- a treatment recommendation system;
- a substitute for clinical judgement;
- a validated patient-safety tool;
- a regulatory compliance certification mechanism.

Outputs should not be used independently to make patient-care decisions.

Any future clinical deployment would require substantially more validation, governance, security review, privacy assessment, human-factors testing, and regulatory analysis.

---

## 26. Security Considerations

Clinical information is highly sensitive.

Any future implementation involving real healthcare data should consider:

- encryption in transit and at rest;
- access control;
- authentication;
- audit logging;
- data minimisation;
- retention controls;
- secure deletion;
- privacy-preserving processing;
- secure software development;
- dependency management;
- vulnerability management;
- model and API security where external AI services are used.

The public research repository should remain free of identifiable patient information.

---

## 27. Governance Considerations

ClinDrift also raises governance questions beyond technical detection performance.

Examples include:

- Who determines which clinical changes are sufficiently significant to trigger alerts?
- Who defines severity?
- Who is accountable when automated transformation introduces an error?
- How should human reviewers interact with automated verification?
- What evidence should be retained for audit?
- How should disagreements between the transformation system, ClinDrift, and a human reviewer be resolved?
- What level of validation should be required before such a mechanism is used clinically?
- How should performance be monitored after deployment?

These questions connect the technical prototype with broader research in trustworthy AI and digital-health governance.

---

## 28. Future Development

Potential future versions of ClinDrift may investigate:

- expanded medication extraction;
- medication-frequency drift;
- diagnosis drift;
- negation changes;
- temporal information drift;
- laboratory-reference-range interpretation;
- omission detection;
- demographic information drift;
- multi-error transformations;
- semantic clinical equivalence;
- FHIR-compatible structured records;
- interoperability with electronic health record systems;
- LLM-based transformation benchmarking;
- comparison with semantic similarity models;
- clinician evaluation;
- larger synthetic benchmark datasets;
- calibrated integrity scoring;
- confidence estimation;
- formal audit trails;
- automated research reports.

These features should be introduced incrementally and evaluated rather than assumed to improve safety.

---

## 29. Reproducibility

Reproducibility is a central design goal.

The repository contains the source code, synthetic examples, mutation mechanisms, and automated tests required to inspect the current prototype.

Core tests can be executed using:

`python -m pytest -v`

Research results reported from future experiments should record:

- ClinDrift version;
- commit identifier;
- Python version;
- dependency versions;
- dataset version;
- mutation configuration;
- evaluation procedure;
- random seed where applicable;
- baseline configuration.

This will make future experiments easier to reproduce and audit.

---

## 30. Open-Source Research Direction

ClinDrift is being developed openly so that its assumptions, rules, limitations, and experimental methods can be inspected.

The long-term research value of the project is not dependent solely on the software interface.

The repository is intended to provide a reproducible research artefact through which questions about information integrity in AI-transformed health records can be investigated.

Future research may extend, challenge, or replace individual components of the prototype.

---

## 31. Research Contribution

At its current stage, ClinDrift should not claim to solve clinical AI hallucination or healthcare AI safety generally.

Its narrower proposed contribution is:

> An open, deterministic and evidence-preserving research framework for detecting and evaluating selected forms of clinically significant information drift introduced during AI transformation of health records.

The framework combines:

- clinically targeted drift detection;
- controlled synthetic mutations;
- evidence traceability;
- severity classification;
- integrity scoring;
- human review;
- automated testing;
- reproducible research outputs.

The significance of this contribution must ultimately be established through systematic experimental evaluation.

---

## 32. Current Prototype Status

ClinDrift v0.1 currently provides the foundation for:

- deterministic drift detection;
- synthetic mutation generation;
- severity-based findings;
- integrity scoring;
- evidence-oriented review;
- human-review workflow;
- downloadable/reportable outputs;
- synthetic sample cases;
- automated core testing.

The existing core test suite currently passes all implemented tests.

This represents a functioning research prototype, not a completed or clinically validated system.

---

## 33. Next Research Milestones

The next research milestones are:

1. formalise the experimental methodology;
2. expand the synthetic evaluation dataset;
3. define controlled mutation scenarios;
4. define ground-truth labels;
5. introduce appropriate baseline methods;
6. evaluate detection performance quantitatively;
7. evaluate integrity-score behaviour;
8. document false positives and false negatives;
9. conduct structured human review where feasible;
10. prepare the resulting methodology and evidence for academic publication.

---

## 34. Conclusion

ClinDrift investigates a narrow but important problem in trustworthy digital health: preserving clinically significant information when AI systems transform health records.

The prototype does not assume that fluent AI-generated clinical text is necessarily faithful clinical text.

Instead, it introduces a verification layer focused on detecting supported changes to clinically relevant facts, preserving evidence for those findings, estimating information integrity, and keeping humans responsible for final interpretation.

ClinDrift v0.1 establishes the technical and research foundation for systematic experimentation.

The next stage is to define the methodology through which that foundation will be evaluated.

---

## Disclaimer

ClinDrift is an experimental research prototype intended for research, education, and controlled evaluation.

It has not been clinically validated and must not be used to diagnose, treat, monitor, or make decisions about patients.

Synthetic data should be used for public demonstrations and repository testing unless appropriate ethical, privacy, security, governance, and regulatory controls have been established for real clinical data.