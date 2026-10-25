# Structured human-oversight study protocol

## Research question

Among clinicians reviewing transformed clinical notes, does ClinDrift's evidence-linked structured review improve detection of seeded integrity errors compared with unaided review, without an unacceptable increase in review time or false alerts?

## Design

Use a counterbalanced within-participant study. Each clinician reviews two disjoint, difficulty-matched case sets:

1. unaided source-versus-note review;
2. ClinDrift-supported review with evidence pairs, severity, verification question, required action and escalation rule.

Randomise condition order and case-set allocation. Include a familiarisation task that is excluded from analysis. Keep the reference labels hidden. Perform an a priori power analysis before recruitment rather than selecting a convenience sample and interpreting non-significance as equivalence.

## Participants and setting

- Recruit Nigerian clinicians across relevant training levels and clinical settings.
- Record role, years of practice, speciality, prior AI-scribe exposure and site type.
- Do not infer reviewer competence from seniority alone.
- Obtain ethics approval and informed consent before collecting participant data.

## Cases

- Use synthetic or appropriately governed, de-identified cases.
- Freeze cases, labels and severity definitions before the main study.
- Include omissions, unsupported additions, medication, dosage, allergy, measurement, negation, duration and laterality errors plus meaning-preserving controls.
- Balance clinically serious and benign cases; do not let overall accuracy hide Critical misses.
- Keep study cases separate from the 140-case development benchmark.

## Outcomes

Primary outcomes:

- sensitivity for all reference integrity errors;
- sensitivity for predeclared Critical errors;
- false-positive rate on meaning-preserving controls;
- review time per case.

Secondary outcomes:

- false-alert burden and proportion escalated;
- reviewer confidence and disposition;
- between-reviewer variation;
- performance by error category, clinician experience and site type;
- usability workload using a predeclared instrument.

Report paired effect estimates with uncertainty intervals. Use a mixed-effects model or another analysis that accounts for repeated observations by clinician and by case. Report missing data and exclusions.

## Safety and interpretation

This is a simulated evaluation, not clinical deployment. ClinDrift prompts may anchor reviewers, create automation bias or increase workload. A positive result supports the tested interface and population only; it does not validate autonomous use or replacement of institutional accountability.
