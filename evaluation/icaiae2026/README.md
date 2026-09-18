# ICAIAE 2026 reproducibility package

This directory supports ICAIAE 2026 Submission #10, **ClinDrift: Evidence-Traceable Integrity Checking for AI-Assisted Clinical Documentation**.

The evaluation is a 140-case synthetic controlled functional stress test. It is not a clinical validation dataset, contains no real patient records, and must not be interpreted as medical-device or hospital-readiness evidence.

## Reproduce

From the repository root:

```bash
python -m pip install -r evaluation/icaiae2026/requirements.txt
python evaluation/icaiae2026/build_and_evaluate.py
```

The evaluator deterministically regenerates the canonical benchmark and writes baseline/current JSONL output snapshots into this directory.

Expected results:

- reconstructed v0.1 baseline: TP=80, TN=20, FP=20, FN=20; precision=0.800; recall=0.800; F1=0.800; specificity=0.500; accuracy=0.714;
- current evaluation configuration: TP=80, TN=40, FP=0, FN=20; precision=1.000; recall=0.800; F1=0.889; specificity=1.000; accuracy=0.857;
- paired case correctness: 20 improved, 0 regressed; exact two-sided McNemar/binomial p=1.9073486328125e-06 (reported as p<0.001).

## Canonical benchmark integrity

Expected SHA-256 for the regenerated `icaiae_benchmark_v1.jsonl`:

`0cca8b673d373b8c73305601e8df2997d34a2334bf0384d5fe0c9a833dbc87ca`

The benchmark contains:

- 80 in-taxonomy positive cases across eight groups;
- 20 out-of-taxonomy challenge positives across unsupported-diagnosis and general semantic-contradiction groups;
- 40 negative controls across unchanged, formatting-equivalent, duration-paraphrase, and frequency-paraphrase groups.

## Failure boundary

The current configuration detects all 80 in-taxonomy positive cases and generates no false alerts on the 40 controls represented here. It detects 0/10 unsupported-diagnosis cases and 0/10 general semantic-contradiction cases. That explicit failure boundary is part of the reported result.

## Scope caution

The benchmark was informed by earlier v0.1 failure observations, especially paraphrase-related false positives. The before/after comparison is therefore a targeted regression evaluation, not an independent estimate of clinical generalisation.
