# Contributing to ClinDrift

ClinDrift is a research prototype for clinical information-integrity assurance. Contributions should improve reproducibility, transparent detection, evaluation, documentation, or safety without turning prototype outputs into clinical claims.

## Useful contribution areas

- add synthetic drift cases for supported or proposed drift categories;
- add negative controls that should not trigger findings;
- improve automated tests and evaluation scripts;
- improve evidence traceability or report clarity;
- improve accessibility and research documentation;
- improve privacy, threat-model, or safe-demo guidance;
- propose narrowly scoped drift detectors with clear assumptions and tests.

## Starter pull requests

Good first contributions include:

- add one synthetic negative control that should not trigger a finding;
- add one controlled mutation fixture for an already supported drift category;
- improve evidence-traceability or report wording without adding clinical claims;
- improve Streamlit accessibility or demo instructions;
- add a unit test for a parsing/comparison edge case;
- improve privacy, threat-model, or reproducibility documentation.

Keep first contributions small and use synthetic or appropriately de-identified data only.

## Data rules

Do not contribute identifiable patient records, clinical screenshots containing personal data, credentials, employer data, or other confidential health information.

Use synthetic or appropriately de-identified examples.

## Workflow

1. Fork the repository.
2. Create a focused branch.
3. Add or update tests for behavioural changes.
4. Run:

```bash
python -m pytest -v
```

5. Open a pull request describing the problem, change, validation, limitations, and any safety implications.

## Research claim discipline

A new detector or passing synthetic test does not establish clinical accuracy, safety, sensitivity, specificity, or regulatory compliance.

Keep controlled mutation results clearly labelled as controlled experiments.

## Pull-request checklist

- [ ] No identifiable patient data is included.
- [ ] Tests pass.
- [ ] New behaviour has tests or a clear rationale.
- [ ] Documentation states limitations.
- [ ] No medical, diagnostic, treatment, certification, or regulatory claim is introduced.
