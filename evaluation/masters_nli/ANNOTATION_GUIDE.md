# Held-Out Benchmark Construction and Annotation Guide

This document defines how the final ClinDrift master's NLI benchmark should be created and frozen.

## Purpose

The benchmark is for **independent evaluation** of candidate semantic-verification models and the final hybrid ClinDrift system. It is not a training set and it is not a clinical-validation dataset.

The final case count and strata should be frozen only after supervisor/peer-review feedback on Chapters 1-3.

## Core rules

1. Do not copy final held-out cases from the existing 140-case development/regression benchmark.
2. Do not tune rules, prompts, thresholds, claim construction, or model choice after looking at final held-out labels and scores.
3. Keep all source text synthetic, openly licensed, or properly de-identified and authorised.
4. Do not place identifiable patient data in GitHub.
5. Give every final benchmark file a SHA-256 hash before candidate comparison begins.
6. Preserve failed and ambiguous cases; do not silently remove cases because a model performs badly.

## Unit of evaluation

Each NLI record contains:
- **premise**: source clinical information available to the checker;
- **hypothesis**: one claim from the transformed/AI-generated documentation;
- **gold label**: contradiction, entailment, or neutral.

Interpretation:
- **entailment**: the source supports the transformed claim;
- **contradiction**: the transformed claim conflicts with the source;
- **neutral**: the source does not provide enough evidence either way.

## Recommended content families

The held-out benchmark should contain unseen wording across:
- medication dosage;
- allergy status;
- duration;
- medication frequency;
- numerical measurements;
- laterality;
- negation;
- omission-related claims;
- unsupported additions;
- diagnosis-level semantic contradictions;
- general semantic contradictions outside the deterministic ontology;
- meaning-preserving paraphrases;
- formatting changes;
- ambiguous/insufficient-evidence cases.

The exact number per group should be fixed before final testing.

## Preventing leakage

A held-out case must not be:
- a trivial rewording of an existing development case that was used to tune the detector;
- generated from the exact same template/value pair used during threshold tuning;
- used to debug model-specific preprocessing;
- inspected selectively after results are produced.

If a held-out case is found to be invalid after the freeze, document:
- the case ID;
- the defect;
- who identified it;
- whether it is excluded;
- the analysis with and without it.

## Gold labels

For deliberately constructed synthetic cases, the NLI relation should be fixed by construction and then independently checked.

Example:
- Source: "Patient takes metformin 500 mg twice daily."
- Claim: "The patient takes metformin 1000 mg twice daily."
- Gold NLI relation: contradiction.

For cases involving medical inference beyond explicit source facts, do not assume the researcher's judgement is sufficient. Mark them for independent clinical/domain review.

## Severity

Severity is **separate** from the NLI label.

A contradiction can be labelled Critical/High/Medium only under a pre-defined rubric. If a clinician has not reviewed the severity rubric, describe severity as a prototype risk-prioritisation scheme rather than a validated clinical-harm scale.

## Annotation fields

Every final case should contain:
- case ID;
- premise;
- hypothesis;
- gold NLI label;
- drift category;
- whether it is a meaning-preserving control;
- provisional severity (if applicable);
- construction/provenance note;
- annotation rationale;
- review/adjudication status.

No annotator names or personal details are required in the public benchmark.

## Independent checking

Minimum:
- one construction label by the researcher;
- one independent label check before freeze;
- disagreements documented and adjudicated.

If two independent raters are available, report agreement (for example Cohen's kappa) before adjudication.

## Freeze procedure

Before the final candidate-model comparison:

1. validate the JSONL schema;
2. confirm that IDs are unique;
3. confirm class counts and category counts;
4. confirm no prohibited personal data is present;
5. compute SHA-256;
6. record the hash in the thesis/repository;
7. make no content changes without creating a new benchmark version and new hash.

## Final reporting

Report:
- class distribution;
- category distribution;
- benchmark provenance;
- annotation procedure;
- disagreements/adjudication;
- dataset hash;
- all candidate results on the same frozen file;
- confidence intervals where feasible;
- paired significance testing where appropriate.

Do not describe benchmark performance as clinical accuracy, diagnostic performance, hospital readiness, or medical-device validation.
