# ICAIAE 2026 Expanded Controlled Evaluation

## Scope

This evaluation extends the original 12-scenario ClinDrift v0.1 baseline into a 140-case synthetic controlled benchmark designed for the ICAIAE 2026 paper. It is a research benchmark, not a clinical validation study.

The benchmark contains 100 positive drift cases and 40 negative controls across the following groups:

- dosage drift: 10
- allergy contradiction: 10
- duration drift: 10
- frequency drift: 10
- measurement drift: 10
- laterality drift: 10
- omission: 10
- supported unsupported-addition cases: 10
- unsupported diagnosis challenge: 10
- general semantic contradiction challenge: 10
- unchanged controls: 10
- formatting-equivalent controls: 10
- duration paraphrase controls: 10
- frequency paraphrase controls: 10

Ground truth was assigned before detector execution. Positive cases contain a deliberately introduced information-integrity error. Negative controls preserve the intended clinical meaning.

## Why canonicalization was added

The original baseline showed false positives for clinically equivalent forms such as `3 days` versus `three days` and `twice a day` versus `twice daily`.

The ICAIAE evaluation branch therefore adds transparent canonicalization for a restricted set of equivalent duration and medication-frequency expressions. This is deliberately deterministic and inspectable.

Examples include:

- `three days` -> `3 days`
- `once per day` -> `once a day`
- `daily` -> `once a day`
- `twice daily` -> `twice a day`
- `once a week` -> `weekly`
- `each night` -> `nightly`

## Results

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

Across the 80 positive cases that fall inside the detector's implemented fact taxonomy, all 80 produced at least one finding in this controlled benchmark.

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

The 30 benchmark cases labelled critical within the supported dosage, allergy and measurement groups were all flagged at case level.

These figures must not be interpreted as clinical sensitivity or medical-device performance. The cases are synthetic, deliberately constructed and aligned to the currently implemented taxonomy.

### Challenge categories

ClinDrift did not detect the 20 challenge cases that required reasoning outside the implemented fact ontology:

| Challenge group | Detection |
|---|---:|
| Unsupported diagnosis statements | 0/10 |
| General semantic contradictions | 0/10 |

These failures are retained as part of the evaluation rather than being hidden. They show that the current deterministic extractor cannot verify arbitrary clinical assertions and should not be described as a comprehensive semantic verifier.

### Negative controls

| Control group | False positives |
|---|---:|
| Unchanged text | 0/10 |
| Formatting-equivalent text | 0/10 |
| Duration paraphrases | 0/10 |
| Frequency paraphrases | 0/10 |

Before the canonicalization change, the same 20 duration/frequency paraphrase controls produced 18 false-positive cases. After the restricted canonicalization layer was added, this fell to 0/20 on this benchmark.

This is evidence of a targeted improvement on the benchmark, not proof that paraphrase-related false positives are solved generally.

## Interpretation for the paper

The expanded controlled benchmark supports four defensible conclusions.

1. A transparent deterministic assurance layer can detect selected, explicitly represented fact-level changes with strong performance inside its implemented taxonomy.
2. Claim-level evidence traceability can be preserved without relying on an opaque end-to-end model.
3. Simple canonicalization can materially reduce false positives caused by known equivalent surface forms.
4. The approach still fails on unsupported diagnoses and general semantic contradictions outside the rule set, which motivates a future hybrid semantic layer rather than an inflated claim of comprehensive clinical verification.

## Reporting cautions

The ICAIAE paper should describe these results as a synthetic controlled evaluation. It should not claim clinical accuracy, diagnostic safety, hospital readiness, medical-device validation, or generalisability to unrestricted clinical language.

The benchmark should be presented as an expanded research baseline whose main purpose is to characterise supported capability and failure boundaries reproducibly.
