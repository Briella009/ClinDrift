# ICAIAE 2026 Expanded Controlled Evaluation

## Scope

This evaluation extends the original 12-scenario ClinDrift v0.1 baseline into a 140-case synthetic controlled benchmark for the ICAIAE 2026 paper. It is a reproducible functional stress test, not a clinical validation study and not an independent external holdout dataset.

The benchmark was designed after the v0.1 baseline had already identified important failure modes, especially paraphrase-related false positives and unsupported semantic content. The expanded benchmark therefore deliberately tests both implemented capabilities and known boundary conditions. Ground-truth labels are encoded independently of detector output for every case.

The benchmark contains 100 positive drift cases and 40 negative controls:

- dosage drift: 10
- allergy contradiction: 10
- duration drift: 10
- frequency drift: 10
- measurement drift: 10
- laterality drift: 10
- omission: 10
- supported transformed-only fact additions: 10
- unsupported diagnosis challenge: 10
- general semantic contradiction challenge: 10
- unchanged controls: 10
- formatting-equivalent controls: 10
- duration paraphrase controls: 10
- frequency paraphrase controls: 10

## Why normalization was added

The original v0.1 baseline showed false positives for clinically equivalent surface forms such as `3 days` versus `three days` and `twice a day` versus `twice daily`. The ICAIAE evaluation branch therefore adds a restricted, inspectable normalization layer for duration and medication-frequency expressions and expands recognition of equivalent frequency forms.

Examples include:

- `three days` -> `3 days`
- `once per day` -> `once a day`
- `daily` -> `once a day`
- `twice daily` -> `twice a day`
- `once a week` -> `weekly`
- `each night` -> `nightly`

The change remains deterministic. It does not introduce an LLM or a general semantic inference model into the ClinDrift detector.

## Current-branch results

### Overall case-level performance

| Metric | Result |
|---|---:|
| Cases | 140 |
| Positive cases | 100 |
| Negative controls | 40 |
| True positives | 80 |
| True negatives | 40 |
| False positives | 0 |
| False negatives | 20 |
| Precision | 1.000 |
| Recall | 0.800 |
| F1 score | 0.889 |
| Specificity | 1.000 |
| Accuracy | 0.857 |

### Supported detector categories

Across the 80 positive cases that fall inside the detector's implemented fact taxonomy, all 80 produced at least one finding.

| Supported group | Detection |
|---|---:|
| Dosage drift | 10/10 |
| Allergy contradiction | 10/10 |
| Duration drift | 10/10 |
| Frequency drift | 10/10 |
| Measurement drift | 10/10 |
| Laterality drift | 10/10 |
| Omission | 10/10 |
| Supported transformed-only fact addition | 10/10 |

The 30 cases in the supported dosage, allergy and blood-pressure measurement groups, which the prototype severity scheme classifies as Critical, were all flagged at case level.

These figures must not be interpreted as clinical sensitivity or medical-device performance. The cases are synthetic, deliberately constructed and substantially aligned with the implemented taxonomy.

### Challenge categories

ClinDrift did not detect the 20 challenge cases requiring reasoning outside its implemented fact ontology:

| Challenge group | Detection |
|---|---:|
| Unsupported diagnosis statements | 0/10 |
| General semantic contradictions | 0/10 |

These failures are retained as part of the evaluation. They show that the current deterministic extractor cannot verify arbitrary clinical assertions and should not be described as a comprehensive semantic verifier.

### Negative controls

| Control group | False positives |
|---|---:|
| Unchanged text | 0/10 |
| Formatting-equivalent text | 0/10 |
| Duration paraphrases | 0/10 |
| Frequency paraphrases | 0/10 |

## Same-benchmark comparison with the v0.1 baseline logic

The same 140 cases were also executed against a reconstruction of the pre-normalization v0.1 extraction logic from the main-branch code. The earlier comparison figures recorded in the first draft of this document were rechecked and corrected before manuscript drafting.

| Metric | v0.1 baseline logic | ICAIAE branch |
|---|---:|---:|
| True positives | 79 | 80 |
| True negatives | 16 | 40 |
| False positives | 24 | 0 |
| False negatives | 21 | 20 |
| Precision | 0.767 | 1.000 |
| Recall | 0.790 | 0.800 |
| F1 score | 0.778 | 0.889 |
| Specificity | 0.400 | 1.000 |
| Accuracy | 0.679 | 0.857 |

Of the 20 dedicated duration/frequency paraphrase controls, 19 were falsely flagged by the v0.1 logic and 0 were falsely flagged after normalization. Five additional formatting-equivalent controls were false positives under the earlier logic. The new branch also resolves one frequency-drift case that the earlier frequency recognizer did not capture.

At the case-correctness level, 25 cases changed from incorrect under the baseline logic to correct under the ICAIAE branch, and no cases changed from correct to incorrect on this benchmark. An exact McNemar test on the discordant case outcomes gives p < 0.001. This paired result is evidence of improvement on this controlled benchmark only; it does not establish external clinical generalization.

## Interpretation for the paper

The benchmark supports four limited but defensible conclusions:

1. A transparent deterministic assurance layer can detect selected, explicitly represented fact-level changes within its implemented taxonomy.
2. Claim-level evidence traceability can be preserved without relying on an opaque end-to-end model.
3. Restricted normalization materially reduces false positives caused by the known equivalent surface forms represented in this benchmark.
4. Unsupported diagnoses and general semantic contradictions remain outside the current rule set, motivating future hybrid semantic verification rather than a claim of comprehensive clinical correctness.

## Reporting cautions

The ICAIAE paper must describe these results as a synthetic controlled evaluation. It must not claim clinical accuracy, diagnostic safety, hospital readiness, medical-device validation, or generalisability to unrestricted clinical language.

The 140-case benchmark is an expanded research baseline and stress test. Because its design was informed by the earlier v0.1 evaluation, the paper should explicitly distinguish it from future independent validation using externally sourced or clinician-annotated clinical data.
