# ICAIAE 2026 Expanded Controlled Evaluation

## Submission alignment

This document records the evaluation used for ICAIAE 2026 Submission #10, **ClinDrift: Evidence-Traceable Integrity Checking for AI-Assisted Clinical Documentation**.

The manuscript itself is not maintained in this repository branch. This branch contains the implementation change and reproducibility artefacts that support the submitted results.

## Scope

The evaluation extends the original 12-scenario ClinDrift v0.1 baseline into a 140-case synthetic controlled benchmark. It is a reproducible functional stress test, not a clinical validation study and not an independent external holdout dataset.

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

## Why normalisation was added

The original v0.1 baseline showed false positives for clinically equivalent surface forms such as `3 days` versus `three days` and `twice a day` versus `twice daily`. The ICAIAE evaluation branch therefore adds a restricted, inspectable normalisation layer for duration and medication-frequency expressions and expands recognition of equivalent frequency forms.

Examples include:

- `three days` -> `3 days`
- `once per day` -> `once a day`
- `daily` -> `once a day`
- `twice daily` -> `twice a day`
- `once a week` -> `weekly`
- `each night` -> `nightly`

The change remains deterministic. It does not introduce an LLM or a general semantic inference model into the ClinDrift detector.

## Current configuration results

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

The 30 supported cases in the dosage, allergy and blood-pressure measurement groups, which the prototype severity scheme classifies as Critical, were all flagged at case level.

These figures must not be interpreted as clinical sensitivity or medical-device performance. The cases are synthetic, deliberately constructed and substantially aligned with the implemented taxonomy.

## Explicit failure boundary

ClinDrift did not detect the 20 challenge cases requiring reasoning outside its implemented fact ontology:

| Challenge group | Detection |
|---|---:|
| Unsupported diagnosis statements | 0/10 |
| General semantic contradictions | 0/10 |

These failures are retained as part of the evaluation. They show that the current deterministic extractor cannot verify arbitrary clinical assertions and should not be described as a comprehensive semantic verifier.

## Negative controls

| Control group | False positives |
|---|---:|
| Unchanged text | 0/10 |
| Formatting-equivalent text | 0/10 |
| Duration paraphrases | 0/10 |
| Frequency paraphrases | 0/10 |

## Same-benchmark comparison with reconstructed v0.1 logic

The same 140 cases were executed against a reconstruction of the pre-normalisation v0.1 extraction behaviour while retaining the same comparison engine. The canonical baseline values used in the submitted manuscript and supplementary evaluation package are:

| Metric | v0.1 baseline logic | Current configuration |
|---|---:|---:|
| True positives | 80 | 80 |
| True negatives | 20 | 40 |
| False positives | 20 | 0 |
| False negatives | 20 | 20 |
| Precision | 0.800 | 1.000 |
| Recall | 0.800 | 0.800 |
| F1 score | 0.800 | 0.889 |
| Specificity | 0.500 | 1.000 |
| Accuracy | 0.714 | 0.857 |

All 10 duration-paraphrase controls and all 10 frequency-paraphrase controls were false positives under reconstructed v0.1 logic. Under the current configuration, all 20 are handled without an alert.

At case-correctness level, **20 cases changed from incorrect under reconstructed v0.1 logic to correct under the current configuration, while 0 cases regressed**. The exact two-sided McNemar/binomial p-value is `1.9073486328125e-06`, reported in the manuscript as **p < 0.001**.

Because these expression families were known v0.1 weaknesses, this paired result is evidence of a successful targeted regression fix on the controlled benchmark. It is not evidence of external clinical generalisation.

## Reproducibility

The canonical benchmark SHA-256 is:

`0cca8b673d373b8c73305601e8df2997d34a2334bf0384d5fe0c9a833dbc87ca`

Repository reproducibility files are stored under `evaluation/icaiae2026/`. The evaluator reconstructs the baseline extraction behaviour internally and evaluates the current branch implementation on the same 140 cases.

Run:

```bash
python -m pip install -r evaluation/icaiae2026/requirements.txt
python evaluation/icaiae2026/build_and_evaluate.py
```

Expected summary:

- baseline: TP=80, TN=20, FP=20, FN=20; precision=0.800; recall=0.800; F1=0.800; specificity=0.500; accuracy=0.714;
- current: TP=80, TN=40, FP=0, FN=20; precision=1.000; recall=0.800; F1=0.889; specificity=1.000; accuracy=0.857;
- paired correctness: 20 improved, 0 regressed; p=1.9073486328125e-06.

## Interpretation and reporting cautions

The benchmark supports four limited conclusions:

1. A transparent deterministic assurance layer can detect selected, explicitly represented fact-level changes within its implemented taxonomy.
2. Claim-level evidence traceability can be preserved without relying on an opaque end-to-end model.
3. Restricted normalisation removes the known duration/frequency paraphrase false positives represented in this benchmark.
4. Unsupported diagnoses and general semantic contradictions remain outside the current rule set, motivating future hybrid semantic verification.

The ICAIAE results must always be described as a **synthetic controlled evaluation**. They must not be presented as clinical accuracy, diagnostic safety, hospital readiness, medical-device validation, or generalisability to unrestricted clinical language.
