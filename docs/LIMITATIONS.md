# ClinDrift Limitations

## Scope, Research Boundaries, Known Limitations, and Responsible Interpretation

**Project:** ClinDrift  
**Version:** v0.1  
**Status:** Research Prototype  
**Repository:** https://github.com/Briella009/ClinDrift

---

## 1. Purpose

This document defines the known limitations and interpretation boundaries of ClinDrift v0.1.

ClinDrift is an open-source research prototype for investigating clinically significant information drift between source clinical information and transformed or AI-generated clinical text.

The project is intentionally narrow.

Its current purpose is to demonstrate and evaluate whether selected changes to clinically relevant facts can be detected transparently while preserving evidence for human review.

ClinDrift should therefore be interpreted as:

> A research prototype for clinical information-integrity assurance.

It should not be interpreted as:

> A clinically validated safety system capable of determining whether a patient record, AI output, diagnosis, treatment, or healthcare decision is correct.

This distinction applies to every result produced by the current prototype.

---

## 2. Research Prototype Status

ClinDrift v0.1 is an experimental software artefact.

It has been developed to support:

- research;
- experimentation;
- software testing;
- synthetic benchmark development;
- academic discussion;
- trustworthy-AI research;
- digital-health security research;
- reproducible evaluation.

The current implementation has not undergone the level of validation required for use in real clinical decision-making.

---

## 3. No Clinical Validation

ClinDrift has not been clinically validated.

Current testing demonstrates software behaviour under controlled conditions.

It does not establish that ClinDrift performs safely or reliably across:

- real electronic health records;
- different hospitals;
- different clinical specialties;
- different patient populations;
- different healthcare systems;
- different documentation styles;
- different AI products;
- different languages;
- complex longitudinal records.

Clinical validation would require a substantially different and more rigorous research process.

---

## 4. No Medical Advice

ClinDrift does not provide medical advice.

The software does not determine:

- appropriate medication;
- appropriate dosage;
- treatment suitability;
- diagnosis;
- prognosis;
- emergency status;
- patient deterioration;
- whether a clinician's decision is correct.

A detected difference means that ClinDrift identified a discrepancy between information supplied as the source and information supplied as the transformed record.

It does not mean that ClinDrift knows which clinical statement is medically correct.

---

## 5. Source Fidelity Is Not Source Truth

One of the most important limitations of ClinDrift is the distinction between fidelity and truth.

ClinDrift asks:

> Was information preserved relative to the supplied source?

ClinDrift does not ask:

> Was the source medically correct in the first place?

For example:

```text
Source:
Patient receives Medication A at 500 mg.

Transformed:
Patient receives Medication A at 500 mg.
```

ClinDrift may identify the dosage as preserved.

This means only that the transformed text retained the value represented in the source.

It does not establish that 500 mg is clinically appropriate.

Therefore:

> ClinDrift measures selected aspects of transformation integrity, not medical correctness.

---

## 6. Compromised Source Records

If the supplied source record is already inaccurate, incomplete, manipulated, or compromised, ClinDrift may preserve that error.

Consider:

```text
Original legitimate information
        ↓
Source is altered
        ↓
Altered source enters ClinDrift
        ↓
Transformation preserves altered information
        ↓
No transformation drift detected
```

ClinDrift cannot currently prove that the supplied source represents an authentic original record.

Future provenance research may address part of this problem.

---

## 7. Narrow Drift Taxonomy

ClinDrift v0.1 intentionally supports only a limited set of clinical information-drift patterns.

Current primary capabilities include:

- medication dosage drift;
- allergy contradiction;
- duration drift.

The prototype also contains limited structured comparison behaviour used in its current tests and interface.

Many clinically important forms of information drift remain outside the current scope.

---

## 8. Unsupported Drift Categories

ClinDrift v0.1 should not be assumed to detect:

- all medication errors;
- medication-frequency drift generally;
- medication-name substitution generally;
- laterality errors;
- diagnosis omission;
- diagnosis substitution;
- procedure changes;
- symptom omission;
- demographic errors;
- temporal-order changes;
- general negation reversal;
- uncertainty removal;
- unsupported clinical additions generally;
- causal distortion;
- patient-identity confusion;
- complex laboratory interpretation errors;
- treatment appropriateness errors.

These are potential future research categories.

---

## 9. Omission Detection Is Limited

Information may disappear during AI summarisation or rewriting.

Examples include omission of:

- an allergy;
- a medication;
- a symptom;
- a warning;
- a diagnosis;
- a laboratory value;
- a treatment duration;
- a clinically relevant qualifier.

ClinDrift v0.1 does not provide comprehensive omission detection.

The absence of an alert should therefore never be interpreted as evidence that all clinically significant information has been preserved.

---

## 10. Negation Understanding Is Limited

Negation can completely reverse medical meaning.

For example:

```text
Patient has chest pain.
```

and:

```text
Patient has no chest pain.
```

represent materially different information.

Although the current prototype addresses a controlled allergy contradiction scenario, ClinDrift v0.1 does not contain comprehensive clinical negation understanding.

General negation drift remains a planned research area.

---

## 11. Temporal Reasoning Is Limited

Clinical records frequently contain time-dependent information.

Examples include:

- previous diagnosis;
- current diagnosis;
- resolved symptoms;
- medications taken historically;
- medications currently prescribed;
- planned procedures;
- completed procedures.

ClinDrift v0.1 does not provide comprehensive temporal reasoning.

A statement that refers to historical information may therefore be interpreted differently from how a clinician would interpret it.

---

## 12. Clinical Uncertainty Is Limited

Healthcare documentation often contains uncertainty.

Examples include:

```text
Possible allergy
```

```text
Suspected infection
```

```text
Rule out pneumonia
```

```text
Patient unsure of medication dose
```

These statements should not automatically be treated as equivalent to confirmed facts.

ClinDrift v0.1 does not comprehensively model uncertainty, probability, or diagnostic confidence.

---

## 13. Contextual Understanding Is Limited

ClinDrift's current deterministic approach focuses on identifiable facts and patterns.

It does not possess complete understanding of:

- patient history;
- clinical reasoning;
- disease progression;
- medication interactions;
- specialty-specific terminology;
- treatment plans;
- broader medical context.

The system may therefore detect a textual difference without understanding its full clinical significance.

---

## 14. Rule-Based Detection Limitations

ClinDrift v0.1 relies heavily on deterministic extraction and comparison logic.

Advantages include transparency and reproducibility.

However, deterministic rules also have limitations.

They may fail when:

- language differs substantially from expected patterns;
- abbreviations are used;
- information is presented in unusual order;
- values are expressed indirectly;
- several medications appear in one sentence;
- multiple clinical concepts share similar formatting;
- clinical shorthand is used;
- complex grammatical structures appear.

These limitations should be evaluated experimentally rather than assumed away.

---

## 15. Extraction Errors

Drift detection depends on extraction.

If the relevant clinical fact is not extracted correctly, downstream comparison may also fail.

Potential extraction failures include:

- missing a medication;
- extracting the wrong dose;
- associating a dose with the wrong medication;
- failing to recognise a duration;
- misunderstanding an allergy statement;
- extracting unrelated numbers.

Therefore:

```text
Extraction error
        ↓
Incorrect structured facts
        ↓
Incorrect comparison
        ↓
Incorrect ClinDrift result
```

Improving detection alone does not solve extraction limitations.

---

## 16. Concept Matching Limitations

Even when values are extracted correctly, they must be matched to the correct clinical concept.

For example, a record may contain several numbers:

```text
Medication A 500 mg
Medication B 20 mg
Temperature 38.2°C
Symptoms for 3 days
```

Incorrect matching may compare unrelated values.

More complex records will therefore require improved concept association.

---

## 17. Multiple Medication Limitation

Clinical records often mention several medications simultaneously.

ClinDrift's current lightweight extraction logic may not always correctly associate:

- medication name;
- dosage;
- frequency;
- duration;
- route.

Multi-medication records should therefore be treated cautiously until systematically evaluated.

---

## 18. Unit Normalisation Is Limited

Equivalent values may be represented using different units.

For example:

```text
500 mg
```

and:

```text
0.5 g
```

can represent the same quantity.

A naive comparison may incorrectly report drift.

ClinDrift should not claim comprehensive unit-equivalence reasoning until corresponding normalization mechanisms are implemented and tested.

---

## 19. Formatting Sensitivity

The current extraction rules may be affected by formatting changes.

Examples include:

- additional spaces;
- punctuation;
- line breaks;
- unusual Unicode;
- decimal representation;
- abbreviations;
- capitalisation;
- special symbols.

Robustness testing is required to determine which formatting variations affect detection.

---

## 20. Semantic Equivalence

Two statements can express the same meaning using different words.

For example:

```text
Symptoms have been present for one week.
```

and:

```text
Symptoms have persisted for seven days.
```

may represent equivalent information.

ClinDrift v0.1 does not claim comprehensive semantic-equivalence reasoning.

Future normalization or semantic methods may improve this capability.

---

## 21. Paraphrasing

AI systems frequently paraphrase records rather than simply replacing values.

Heavy paraphrasing may make deterministic extraction more difficult.

A transformed record may preserve the meaning but use terminology that is not recognised by the current extractor.

This may create false-positive or false-negative findings.

---

## 22. False Positives

ClinDrift can produce false positives.

A false positive occurs when ClinDrift reports clinically significant drift even though the relevant information has been preserved.

Potential causes include:

- equivalent units;
- synonymous wording;
- formatting differences;
- extraction mistakes;
- context differences;
- ambiguous language.

False positives matter because excessive alerts may create:

- unnecessary review;
- loss of user confidence;
- alert fatigue;
- increased operational burden.

---

## 23. False Negatives

ClinDrift can produce false negatives.

A false negative occurs when clinically relevant information changes but ClinDrift does not detect the change.

Potential causes include:

- unsupported drift type;
- extraction failure;
- unusual phrasing;
- complex clinical context;
- adversarial formatting;
- multiple competing values;
- incomplete rule coverage.

False negatives are especially important in safety-oriented evaluation and must be documented openly.

---

## 24. Current 3/3 Self-Test Limitation

ClinDrift's built-in Mutation Lab currently demonstrates successful detection of three deliberately injected mutations.

The demonstration may report:

```text
Injected mutations: 3
Detected mutations: 3
Detection rate: 100%
```

This result applies only to those deliberately constructed mutations.

It does not mean that ClinDrift is 100% accurate.

It does not establish:

- clinical sensitivity;
- clinical specificity;
- general real-world performance;
- performance on unseen records;
- performance on all mutation categories;
- regulatory validation.

The 3/3 result should always be described as a controlled self-test.

---

## 25. Current Unit-Test Limitation

The current v0.1 automated test baseline contains four core tests.

They currently cover:

- dosage drift detection;
- preserved measurement behaviour;
- allergy contradiction detection;
- duration drift detection.

Passing four tests confirms that the current functions behave as expected for those test cases.

It does not establish general performance.

A larger independent benchmark is required.

---

## 26. Synthetic Dataset Limitation

The initial research strategy uses synthetic clinical records.

Synthetic data provide privacy and experimental-control advantages.

However, synthetic examples may be:

- cleaner;
- shorter;
- less ambiguous;
- more structured;
- less noisy;
- more predictable

than real clinical documentation.

Performance on synthetic data may therefore overestimate real-world performance.

---

## 27. Benchmark Construction Bias

If benchmark cases are designed using the same patterns used to develop ClinDrift, evaluation results may be artificially strong.

This is a form of test leakage.

To reduce this risk, future evaluation should separate:

```text
Development examples
```

from:

```text
Held-out evaluation examples
```

Final research performance should not rely entirely on examples used while writing detection rules.

---

## 28. Limited Sample Size

The current four unit tests and three controlled mutations are intentionally small.

They are suitable for basic software verification.

They are not sufficient for strong statistical conclusions.

The planned larger synthetic benchmark is intended to provide more meaningful experimental evidence.

---

## 29. No Independent Benchmark Yet

ClinDrift v0.1 has not yet been evaluated against a large independent benchmark.

Therefore the project cannot currently make defensible claims about:

- overall precision;
- overall recall;
- overall F1 score;
- clinical sensitivity;
- clinical specificity;
- general error-detection accuracy.

These metrics should only be reported after the planned benchmark has actually been executed.

---

## 30. No External Validation Yet

The current prototype has not been independently validated by:

- an external research group;
- a hospital;
- a healthcare organisation;
- a clinical informatics team;
- a regulatory body.

Independent evaluation would strengthen future research claims.

---

## 31. No Clinical Expert Evaluation Yet

The current technical prototype has not yet undergone structured evaluation by clinical experts.

Future clinician evaluation may be needed to assess:

- clinical relevance of findings;
- appropriateness of severity;
- meaningfulness of detected changes;
- acceptable false-positive rates;
- important missed errors;
- usefulness of evidence presentation.

Software correctness and clinical usefulness are not the same thing.

---

## 32. Severity Is Heuristic

ClinDrift currently assigns severity to findings using prototype rules.

For example, an allergy contradiction may receive a critical classification.

These severity categories are useful for demonstrating prioritisation logic.

However, the current severity system has not been clinically validated.

Severity should therefore be described as:

> A prototype prioritisation heuristic.

It should not be interpreted as an independently validated estimate of patient harm.

---

## 33. Integrity Score Is Experimental

ClinDrift generates an integrity score.

This score summarises detected transformation drift according to current scoring rules.

The score is not:

- a probability of patient harm;
- a medical-risk score;
- a diagnostic confidence score;
- a clinical safety certification;
- a regulatory risk rating.

A score of:

```text
100/100
```

does not prove that a clinical record is safe or medically correct.

It means only that the currently implemented detection logic did not identify score-reducing supported findings in that comparison.

---

## 34. High Integrity Does Not Equal Clinical Safety

This limitation is particularly important.

A record may receive a high integrity score while containing:

- incorrect source information;
- an unsupported diagnosis change;
- an omission ClinDrift cannot detect;
- a laterality error;
- a frequency error;
- a clinically dangerous change outside the implemented taxonomy.

Therefore:

> High information-preservation confidence within ClinDrift's current scope must not be interpreted as overall clinical safety.

---

## 35. Human Review Remains Necessary

ClinDrift is designed to support human review.

It is not designed to remove human judgement from clinical workflows.

Human verification remains necessary because:

- context matters;
- extraction may fail;
- unsupported errors may exist;
- detected differences may be legitimate;
- severity may require clinical interpretation;
- source information may itself be inaccurate.

The intended model is:

```text
Automated detection
        +
Evidence
        +
Human judgement
```

rather than:

```text
Automated detection
        =
Clinical decision
```

---

## 36. Human Review Is Also Fallible

Human review is not automatically correct.

Reviewers may:

- overlook evidence;
- misunderstand context;
- experience alert fatigue;
- trust automation excessively;
- reject correct findings;
- approve incorrect transformations.

Future human-factors research should therefore evaluate the interaction between ClinDrift and reviewers.

---

## 37. Automation Bias

Users may trust an automated system simply because it produces a structured score or polished interface.

For example:

```text
Integrity Score: 100/100
```

may appear authoritative.

This creates automation-bias risk.

ClinDrift's interface and documentation should continue to communicate that the score reflects only implemented rules and evaluated conditions.

---

## 38. Alert Fatigue

A system that generates too many warnings may cause users to ignore them.

Future evaluation should therefore measure:

- false-positive rate;
- findings per document;
- unnecessary review burden;
- reviewer acceptance or rejection patterns.

High detection alone does not establish practical usefulness.

---

## 39. No Medical-Device Claim

ClinDrift v0.1 is not presented as a medical device.

The project does not claim:

- regulatory approval;
- regulatory clearance;
- clinical certification;
- medical-device registration;
- authorisation for clinical deployment.

Any future medical-device classification would depend on intended use, functionality, jurisdiction, and applicable regulation.

---

## 40. No Regulatory Compliance Determination

ClinDrift does not certify compliance with:

- UK regulatory requirements;
- Canadian regulatory requirements;
- data-protection law;
- healthcare cybersecurity standards;
- AI governance frameworks;
- medical-device regulations.

Future research may map ClinDrift capabilities to selected guidance or assurance principles.

Such mapping should not be described as compliance certification.

---

## 41. UK Context Is Research Context

ClinDrift includes a UK research context because the project is relevant to questions involving:

- AI-assisted healthcare;
- clinical information safety;
- trustworthy AI;
- human oversight;
- privacy;
- cybersecurity;
- evidence traceability.

This does not mean that ClinDrift has been approved for NHS use or certified against UK requirements.

Any future UK regulatory discussion should use current authoritative sources and distinguish research interpretation from legal or regulatory advice.

---

## 42. Canadian Context Is Research Context

ClinDrift also includes a Canadian research context.

Relevant research themes include:

- AI-assisted documentation;
- AI scribes;
- interoperable patient information;
- privacy;
- cybersecurity;
- human oversight;
- trustworthy healthcare AI.

This does not mean that ClinDrift has been approved by Health Canada or validated for use within Canadian healthcare.

---

## 43. No Real-Time Monitoring

ClinDrift v0.1 does not continuously monitor clinical systems.

It analyses supplied source and transformed text.

It does not currently provide:

- continuous EHR surveillance;
- real-time hospital monitoring;
- automatic alert escalation;
- SOC integration;
- SIEM integration;
- medical-device monitoring.

---

## 44. No EHR Integration

The current prototype does not integrate directly with production electronic health record systems.

It does not currently provide:

- Epic integration;
- Cerner integration;
- hospital database access;
- production HL7 ingestion;
- production FHIR workflows.

FHIR-related functionality remains a potential future research direction.

---

## 45. No Production Authentication

ClinDrift v0.1 does not provide a full healthcare identity-and-access-management architecture.

It should not be assumed to contain:

- enterprise single sign-on;
- clinician identity verification;
- role-based clinical access;
- patient-level authorisation;
- privileged-access management;
- multi-factor authentication.

Such controls would be essential for handling real patient information in a production environment.

---

## 46. No Production Audit Architecture

The application can generate audit-style output.

However, this is not the same as a hardened immutable audit system.

The current prototype does not claim:

- cryptographic audit-log integrity;
- legally defensible chain of custody;
- tamper-evident storage;
- enterprise log retention;
- signed clinical reports.

Future work may investigate these properties.

---

## 47. Report Tampering

Downloaded reports can potentially be altered after they leave ClinDrift.

A modified report may no longer correspond to the analysis that generated it.

Future security mechanisms could include:

- content hashing;
- digital signatures;
- unique report identifiers;
- software version identifiers;
- signed timestamps.

These protections are not currently claimed.

---

## 48. Provenance Limitation

ClinDrift v0.1 does not provide comprehensive provenance verification.

It may not know whether source information originated from:

- a clinician;
- an AI model;
- a patient;
- an EHR;
- copied documentation;
- a manipulated source.

Future work may investigate cryptographic or metadata-based provenance mechanisms.

---

## 49. Prompt Injection Is Not Currently Detected

Prompt injection is a relevant threat when AI systems process untrusted text.

ClinDrift v0.1 does not currently provide dedicated prompt-injection detection.

If an upstream AI system is manipulated by embedded instructions, ClinDrift may detect some resulting factual changes if they fall within supported drift categories.

However, it does not currently identify the malicious instruction itself.

---

## 50. General Hallucination Detection Is Not Implemented

AI-generated clinical text may contain information that never existed in the source.

ClinDrift does not currently provide comprehensive hallucination detection.

Some hallucinations may manifest as detectable structured drift.

Others may not.

General unsupported-addition detection is planned for future versions.

---

## 51. Adversarial Robustness Is Not Established

ClinDrift has not yet undergone extensive adversarial testing.

An attacker may deliberately construct input intended to bypass extraction or detection.

Potential techniques include:

- unusual spacing;
- punctuation manipulation;
- contradictory statements;
- Unicode tricks;
- ambiguous units;
- multiple competing values;
- unusual sentence structure.

Adversarial robustness must be measured rather than assumed.

---

## 52. Input Validation Is Research Grade

The current user interface is designed primarily for controlled research and demonstrations.

Input validation has not been presented as equivalent to a production healthcare security gateway.

Future deployments may require:

- maximum input sizes;
- stricter type validation;
- malicious-content filtering;
- resource limits;
- upload validation;
- content security controls.

---

## 53. Availability Is Not Guaranteed

ClinDrift is not currently designed with high-availability healthcare infrastructure.

The application may become unavailable because of:

- hosting outages;
- software errors;
- dependency failures;
- network issues;
- resource exhaustion;
- deployment maintenance.

ClinDrift must not be relied upon as a safety-critical availability dependency in its current form.

---

## 54. Performance at Scale Is Unknown

The current prototype has not been benchmarked across:

- millions of records;
- long clinical histories;
- high concurrent user volumes;
- large document batches;
- production healthcare workloads.

Performance and scalability remain future engineering questions.

---

## 55. Language Limitation

ClinDrift v0.1 is primarily designed around English-language text.

It has not been validated for:

- French;
- German;
- Spanish;
- Arabic;
- African languages;
- multilingual clinical records.

Translation can itself introduce information drift.

Multilingual assurance may be a valuable future research direction.

---

## 56. Specialty Limitation

Different medical specialties use different terminology and documentation structures.

ClinDrift has not been independently validated for specialties such as:

- cardiology;
- oncology;
- paediatrics;
- psychiatry;
- obstetrics;
- surgery;
- radiology;
- emergency medicine.

Future evaluation should avoid assuming uniform performance across clinical domains.

---

## 57. Documentation-Length Limitation

The current demonstrations use relatively short clinical passages.

Long records introduce challenges such as:

- repeated medications;
- historical information;
- contradictory notes;
- copied-forward content;
- repeated measurements;
- temporal relationships;
- multiple clinicians.

Performance on long records remains unestablished.

---

## 58. Structured vs Unstructured Data

ClinDrift currently focuses primarily on text comparison.

Health systems also contain structured information such as:

- medication tables;
- coded diagnoses;
- laboratory tables;
- observations;
- FHIR resources.

Structured comparison may be more reliable for some information types.

Future ClinDrift architecture may combine structured and unstructured verification.

---

## 59. AI Transformation Models Are Not Yet Benchmarked

The current research prototype focuses primarily on controlled transformations and mutations.

It has not yet been systematically benchmarked across multiple external AI models.

Therefore ClinDrift cannot currently claim to evaluate the relative safety of:

- commercial LLMs;
- open-source LLMs;
- clinical foundation models;
- AI scribe products;
- summarisation products.

Such comparison would require a separate experiment.

---

## 60. Model Updates May Affect Future Research

If future experiments use external AI models, those models may change over time.

A provider may update:

- model weights;
- safety policies;
- system prompts;
- infrastructure;
- output behaviour.

This can reduce reproducibility.

Future experiments should record:

- model name;
- model version where available;
- provider;
- date;
- prompt;
- generation parameters.

---

## 61. No Causal Attribution

If ClinDrift detects drift, it cannot necessarily determine why the drift occurred.

Possible causes include:

- AI hallucination;
- human editing;
- malicious manipulation;
- integration error;
- transcription error;
- source ambiguity;
- formatting transformation.

ClinDrift identifies a difference.

It does not currently provide reliable causal attribution.

---

## 62. Security Detection Boundary

ClinDrift is not a general cybersecurity monitoring platform.

It does not currently detect:

- malware;
- ransomware;
- account compromise;
- network attacks;
- credential theft;
- endpoint compromise;
- phishing;
- lateral movement.

Its cybersecurity contribution is specifically connected to information integrity, AI assurance, provenance, privacy, and manipulation of transformed clinical content.

---

## 63. Privacy Boundary

ClinDrift's public research workflow should use synthetic information.

The application should not be treated as automatically suitable for identifiable patient data.

Real health information may require controls involving:

- lawful processing;
- consent or other legal basis;
- data minimisation;
- secure storage;
- access control;
- retention;
- deletion;
- audit;
- contractual arrangements;
- institutional approval.

These controls are outside the current public prototype.

---

## 64. Public Deployment Limitation

A public Streamlit deployment increases accessibility.

It does not convert ClinDrift into a production health application.

The public version should be treated as:

> A demonstration and research interface.

Users should be explicitly discouraged from entering real identifiable patient information.

---

## 65. Third-Party Hosting

If ClinDrift is hosted on third-party infrastructure, the platform becomes part of the data-processing environment.

This may affect:

- data location;
- logging;
- availability;
- privacy;
- security.

For the public research version, synthetic information should be used.

---

## 66. External API Limitation

ClinDrift v0.1 does not require external clinical AI services for its core deterministic drift detection.

If external AI APIs are introduced later, additional considerations will include:

- API credentials;
- transmission security;
- third-party retention;
- provider privacy terms;
- model training policies;
- cross-border transfers;
- availability;
- cost;
- reproducibility.

The threat and privacy models must be updated before such functionality is treated as production-ready.

---

## 67. Open-Source Limitations

Open source improves transparency, but it does not guarantee correctness.

Public code may still contain:

- bugs;
- insecure assumptions;
- incomplete rules;
- vulnerable dependencies;
- design mistakes.

Users and researchers should independently inspect and test the software.

---

## 68. Dependency Risk

ClinDrift relies on third-party Python packages.

Dependencies may contain vulnerabilities or change behaviour after updates.

The current prototype should continue to use:

- documented dependencies;
- controlled upgrades;
- automated regression tests;
- vulnerability review as maturity increases.

---

## 69. Python-Version Compatibility

The prototype has been developed and tested in its current development environment.

Other Python versions or operating systems may behave differently.

Reproducible research should therefore record:

- Python version;
- dependency versions;
- operating system where relevant;
- ClinDrift version;
- Git commit.

---

## 70. Research Reproducibility Limitations

Even open-source experiments can fail to reproduce if:

- dependencies change;
- datasets change;
- code changes;
- environment details are missing;
- benchmark labels are changed;
- experimental procedures are undocumented.

Future formal experiments should therefore reference exact commits and benchmark versions.

---

## 71. No Statistical Claims Yet

ClinDrift should not currently claim statistically established performance.

Until the larger benchmark is executed, metrics such as:

- precision;
- recall;
- F1;
- false-positive rate;
- confidence intervals

remain to be measured.

Any future reported number must be linked to the dataset and conditions under which it was obtained.

---

## 72. No Superiority Claim

ClinDrift has not yet been shown to outperform:

- semantic similarity;
- embedding-based comparison;
- LLM reviewers;
- other clinical NLP systems;
- commercial healthcare assurance products.

Comparison experiments are planned research work.

The project's transparency and architecture should not be confused with demonstrated superior performance.

---

## 73. No Generalisability Claim

Successful results on one benchmark do not automatically generalise to all healthcare environments.

Generalisability must be evaluated across:

- datasets;
- specialties;
- organisations;
- document types;
- AI systems;
- healthcare jurisdictions.

---

## 74. No Patient-Safety Outcome Evidence

ClinDrift has not been evaluated for its effect on actual patient outcomes.

There is currently no evidence that ClinDrift:

- reduces adverse events;
- reduces prescribing errors;
- reduces mortality;
- improves treatment outcomes;
- reduces clinician workload.

Such claims would require dedicated clinical studies.

---

## 75. No Workflow-Effectiveness Evidence

ClinDrift has not yet been evaluated inside real clinical workflows.

Unknown factors include:

- reviewer workload;
- response time;
- alert fatigue;
- usability;
- workflow interruption;
- clinician trust;
- adoption.

Human-factors evaluation should therefore be considered separately from algorithmic evaluation.

---

## 76. Human-Factors Limitations

A technically accurate alert may still be ineffective if:

- it is difficult to understand;
- it appears at the wrong time;
- it provides insufficient evidence;
- there are too many alerts;
- clinicians misunderstand the score.

Future evaluation should study human interaction with ClinDrift.

---

## 77. Explainability Boundary

ClinDrift aims for transparency through source-to-transformed evidence traceability.

This is useful, but it does not solve all explainability problems.

A reviewer may still need to understand:

- why a rule exists;
- whether the rule is clinically justified;
- how severity was chosen;
- how the score was calculated;
- whether context changes interpretation.

Explainability should therefore include both evidence and documentation of system logic.

---

## 78. Evidence Can Be Incomplete

A detected value may be correct while the displayed evidence lacks sufficient surrounding context.

Future work may need to improve:

- sentence-level evidence;
- document location;
- structured provenance;
- evidence highlighting;
- contextual excerpts.

Evidence traceability is a design objective, not an already perfected capability.

---

## 79. Auditability Boundary

ClinDrift provides inspectable findings and downloadable output.

However, research auditability differs from legal, regulatory, or forensic auditability.

The current reports should not be described as:

- legally immutable records;
- certified audit evidence;
- forensic chain-of-custody artefacts;
- regulatory attestations.

---

## 80. Research Ethics

The use of synthetic data reduces many risks but does not remove all research responsibilities.

Future studies involving:

- patient records;
- clinicians;
- healthcare organisations;
- identifiable information;
- clinical workflows

may require formal ethics and governance review.

---

## 81. Bias Considerations

ClinDrift's deterministic rules may reflect the examples and assumptions used during development.

Potential biases may include:

- English-language bias;
- documentation-style bias;
- medication-format bias;
- benchmark-construction bias;
- specialty bias.

Future benchmark development should deliberately introduce diversity.

---

## 82. Limited Fairness Evaluation

The current prototype does not make patient-level predictions and therefore differs from conventional predictive medical AI.

Nevertheless, future use with clinical documentation could still produce uneven performance across:

- languages;
- documentation styles;
- regions;
- healthcare institutions.

Fairness and robustness should be evaluated if ClinDrift expands into broader clinical use.

---

## 83. Version-Specific Results

Every performance result should be considered version-specific.

For example:

```text
ClinDrift v0.1
```

may behave differently from:

```text
ClinDrift v0.2
```

because extraction rules, drift taxonomy, scoring, and evidence handling may change.

Research publications should reference exact versions.

---

## 84. Planned Features Are Not Current Features

The roadmap includes potential capabilities such as:

- laterality drift;
- medication-frequency drift;
- unsupported additions;
- omission detection;
- prompt-injection analysis;
- privacy leakage indicators;
- provenance assurance.

These are research directions.

They must not be represented as implemented until code and corresponding tests exist.

---

## 85. Future Machine-Learning Components

If ClinDrift later incorporates machine learning or LLM-based reasoning, new limitations will arise.

These may include:

- non-determinism;
- hallucination;
- model bias;
- prompt sensitivity;
- model updates;
- training-data limitations;
- explainability challenges;
- external API dependence.

The introduction of AI into the verifier would therefore require additional evaluation.

---

## 86. Verification-System Independence

A broader research question concerns whether the verifier should use the same type of AI technology as the system being verified.

If both transformation and verification depend on similar generative models, correlated failures may occur.

ClinDrift's current deterministic baseline avoids some of this dependency.

Future hybrid approaches should evaluate independence carefully.

---

## 87. Residual Risk

Even after significant future development, ClinDrift will not eliminate all risk.

Residual risk may remain because of:

- unknown clinical context;
- unseen language patterns;
- compromised sources;
- novel attacks;
- human error;
- model error;
- software vulnerabilities;
- unsupported drift categories.

ClinDrift should therefore remain one assurance layer rather than a complete safety solution.

---

## 88. Responsible Current Claims

ClinDrift v0.1 can currently be described as:

> An open-source research prototype for detecting selected forms of clinically significant information drift between source and transformed health information.

It may also be stated that the current prototype:

- implements controlled dosage-drift detection;
- implements controlled allergy-contradiction detection;
- implements controlled duration-drift detection;
- provides evidence traceability;
- calculates an experimental integrity score;
- retains human review;
- includes a controlled Mutation Lab;
- currently passes four core automated tests;
- detects the three mutations in its built-in controlled demonstration.

---

## 89. Claims That Should Not Currently Be Made

ClinDrift should not currently be described as:

- clinically validated;
- production ready;
- medically certified;
- 100% accurate;
- capable of detecting all clinical AI errors;
- capable of preventing patient harm;
- a replacement for clinicians;
- regulatory compliant by default;
- approved for hospital deployment;
- a medical device;
- an autonomous clinical safety system.

---

## 90. Recommended Disclaimer for Public Demonstrations

The following principle should remain visible in the public application:

> **Research prototype only. ClinDrift does not diagnose patients, certify AI systems, or determine regulatory compliance. Human clinical verification remains required.**

A public deployment should also discourage users from submitting identifiable patient data.

---

## 91. Research Interpretation Principle

All ClinDrift results should be interpreted according to:

```text
What was tested
+
How it was tested
+
Which version was tested
+
Which data were used
+
Which drift categories were supported
=
What can reasonably be claimed
```

Anything beyond that evidence should be described as future research rather than demonstrated capability.

---

## 92. Limitation Reporting in Publications

Any academic paper based on ClinDrift should clearly disclose:

- prototype status;
- synthetic-data use;
- benchmark size;
- drift categories evaluated;
- test-set construction;
- development/evaluation separation;
- lack of clinical validation;
- false positives;
- false negatives;
- unsupported error classes;
- clinical expert involvement or absence;
- software version;
- benchmark version.

Negative results and system failures should be reported alongside successful results.

---

## 93. Limitation Reporting in Presentations

Conference presentations should avoid presenting demonstration performance as broad clinical performance.

For example:

Appropriate:

> The built-in controlled self-test detected all three injected v0.1 mutations.

Not appropriate:

> ClinDrift detects 100% of clinical errors.

Research communication should remain precise.

---

## 94. Limitation Reporting on CVs and Portfolios

ClinDrift may appropriately be described as:

> Designed and developed an open-source research prototype for clinical information-integrity assurance, combining deterministic drift detection, controlled mutation testing, evidence traceability, integrity scoring, and human-review safeguards.

Descriptions should avoid implying clinical deployment or validated medical effectiveness unless future evidence supports those claims.

---

## 95. Limitation Reporting in PhD Applications

ClinDrift can demonstrate research capability in:

- trustworthy AI;
- cybersecurity;
- digital health;
- software development;
- research methodology;
- reproducibility;
- AI governance;
- clinical information integrity;
- human-centred assurance.

Its strongest academic positioning is as an evolving research artefact rather than a finished commercial healthcare product.

---

## 96. Future Work Required Before Real-World Clinical Research

Before meaningful real-world clinical evaluation, future work may require:

1. expanded drift taxonomy;
2. larger synthetic benchmark;
3. independent held-out evaluation;
4. error analysis;
5. baseline comparison;
6. improved clinical NLP;
7. structured clinical expert review;
8. privacy assessment;
9. security assessment;
10. ethics and governance review where required;
11. usability testing;
12. provenance mechanisms;
13. deployment controls;
14. monitoring strategy.

---

## 97. Future Work Required Before Production Deployment

Production deployment would require substantially more than successful research evaluation.

Potential requirements include:

- enterprise authentication;
- authorisation;
- encryption;
- secure hosting;
- audit logging;
- monitoring;
- incident response;
- data retention controls;
- backup and recovery;
- vulnerability management;
- privacy governance;
- clinical safety review;
- regulatory analysis;
- human-factors validation;
- organisational accountability.

These requirements are outside v0.1.

---

## 98. Current Research Value Despite Limitations

The limitations documented here do not remove the research value of ClinDrift.

Instead, they define the exact problem the project is currently equipped to investigate.

ClinDrift provides a platform for asking:

> Can clinically important changes be detected transparently and reproducibly when AI transforms health information?

The current prototype provides:

- an implementable hypothesis;
- a working detector;
- controlled mutations;
- evidence traceability;
- testable outcomes;
- a methodology;
- an evaluation plan;
- a threat model;
- a path toward larger experiments.

The limitations indicate where further evidence is needed.

---

## 99. Core Limitation Principle

The central limitation principle of ClinDrift is:

> **Absence of detected drift is not proof of clinical correctness.**

A second principle is:

> **Detection of drift identifies a discrepancy, not the medically correct resolution of that discrepancy.**

A third principle is:

> **ClinDrift should only be trusted within the scope that has actually been implemented and empirically evaluated.**

---

## 100. Conclusion

ClinDrift v0.1 is an early-stage research prototype focused on a narrow but important trustworthy-AI problem: preserving clinically significant information during automated transformation.

The prototype currently demonstrates that selected structured changes can be detected using transparent deterministic mechanisms while preserving evidence for human review.

However, the system remains limited by:

- narrow rule coverage;
- limited clinical-language understanding;
- synthetic evaluation;
- small current test coverage;
- lack of independent clinical validation;
- experimental severity and scoring;
- absence of production security architecture;
- incomplete semantic and contextual reasoning.

These limitations are intentionally documented rather than hidden.

The objective of ClinDrift research is not to pretend that the current prototype solves clinical AI safety.

The objective is to build a transparent, testable and reproducible foundation through which increasingly difficult information-integrity questions can be investigated systematically.

---

## Disclaimer

ClinDrift is an experimental research prototype intended for research, education, software testing, and controlled academic evaluation.

It has not been clinically validated, approved as a medical device, or certified for clinical use.

ClinDrift must not be used independently for diagnosis, treatment, medication management, patient monitoring, or autonomous clinical decision-making.

A ClinDrift result describes only the behaviour of the implemented information-integrity checks under the supplied input and should not be interpreted as proof that a clinical record is medically correct or safe.

Public demonstrations should use synthetic information unless appropriate ethical, privacy, legal, security, clinical, and governance controls have been established.