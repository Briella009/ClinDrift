# ClinDrift

**Clinical Information Integrity Assurance**

ClinDrift is an open-source research prototype for detecting safety-relevant semantic drift between source clinical information and transformed or AI-generated clinical text.

The project investigates one central question:

> **Did clinically important meaning survive when health information was transformed?**

ClinDrift focuses on information integrity, evidence traceability, transparent detection, reproducible evaluation, and human oversight.

> **Research prototype only. ClinDrift does not diagnose patients, certify AI systems, or determine regulatory compliance. Human clinical verification remains required.**

---

## Why ClinDrift Exists

AI systems are increasingly being used to summarise, rewrite, structure, and transform health information.

A clinically important fact can change during that transformation while the resulting text still appears plausible.

For example:

- a medication dose may change from **500 mg to 1000 mg**
- a documented **penicillin allergy** may become **no known drug allergies**
- a symptom duration may change from **3 days to 3 weeks**

These are information-integrity failures.

ClinDrift provides an experimental assurance layer for comparing source clinical information with transformed information and identifying supported forms of clinically significant drift.

---

## Current v0.1 Capabilities

ClinDrift v0.1 currently provides:

- medication dosage drift detection
- allergy contradiction detection
- duration drift detection
- preservation checks for supported measurements
- severity classification
- transparent integrity scoring
- claim-level evidence traceability
- human-review signalling
- controlled mutation generation
- mutation detection self-testing
- downloadable JSON audit reports
- UK and Canada research context
- documented research methodology
- explicit prototype limitations

---

## Controlled Mutation Lab

ClinDrift contains a built-in **Clinical Drift Mutation Lab**.

The Mutation Lab deliberately introduces known errors into clean clinical information so that the detection engine can be evaluated against controlled changes.

The current mutation set includes:

| Mutation type | Original value | Mutated value |
| --- | --- | --- |
| Dosage drift | 500 mg | 1000 mg |
| Allergy contradiction | penicillin | No known drug allergies |
| Duration drift | 3 days | 3 weeks |

These changes are deliberately introduced by ClinDrift for controlled integrity testing.

---

## Example Controlled Evaluation

Using the current built-in controlled mutation case, ClinDrift produced:

| Metric | Result |
| --- | ---: |
| Injected mutations | 3 |
| Detected mutations | 3 |
| Controlled mutation detection rate | 100% |
| Findings | 3 |
| Critical findings | 2 |
| Integrity score | 54/100 |
| Review status | Human review required |

**Important:** the 100% detection rate refers only to the current controlled three-mutation self-test.

It is **not** a claim that ClinDrift has 100% clinical accuracy, sensitivity, or generalisable performance.

Larger benchmark evaluation is planned for future research versions.

---

## Evidence Traceability

ClinDrift is designed so that an automated flag is not presented without supporting context.

Each supported finding can contain:

- drift type
- severity
- source value
- transformed value
- source evidence
- transformed evidence
- human-readable rationale

For example, an allergy contradiction can show:

**Source**

`Value: penicillin`

Evidence:

`Patient is allergic to penicillin.`

**Transformed**

`Value: no known drug allergies`

Evidence:

`No known drug allergies.`

ClinDrift then explains why the transformation was flagged.

This creates claim-level traceability between the automated finding and the clinical information that produced it.

---

## Architecture

ClinDrift v0.1 follows this processing flow:

```text
Source clinical information
            |
            v
    Clinical fact extraction
            |
            v
        Source facts
            |
            |
            +-------------------------+
                                      |
Transformed / AI-generated text       |
            |                         |
            v                         |
    Clinical fact extraction          |
            |                         |
            v                         |
     Transformed facts                |
            |                         |
            +------------+------------+
                         |
                         v
                   Drift engine
                         |
                         v
               Severity + evidence
                         |
                         v
                 Integrity scoring
                         |
                         v
               Human review status
                         |
                         v
              Downloadable report
```

---

## Project Structure

```text
ClinDrift-v0.1/
│
├── app.py
├── README.md
├── requirements.txt
├── VERSION
├── .gitignore
│
├── .streamlit/
│   └── config.toml
│
├── data/
│
├── src/
│   ├── extractor.py
│   ├── drift_engine.py
│   ├── scoring.py
│   └── mutations.py
│
└── tests/
    └── test_core.py
```

---

## Core Workflow

The current ClinDrift workflow is:

1. Provide the original source clinical information.
2. Provide transformed or AI-generated clinical information.
3. Optionally use the Mutation Lab to introduce controlled errors.
4. Run the integrity check.
5. ClinDrift extracts supported clinical facts.
6. Source and transformed facts are compared.
7. Supported information drift is detected.
8. Findings are assigned severity.
9. Evidence is linked to each finding.
10. An integrity score is calculated.
11. Human review is requested when safety-relevant drift is detected.
12. An audit report can be downloaded.

---

## Integrity Assessment

ClinDrift provides an integrity assessment containing:

- integrity score
- number of findings
- number of critical findings
- overall risk level
- review status
- detected drift
- supporting evidence

The score is a transparent prototype assurance signal.

It is **not** a clinical safety certification.

A high score means that the current v0.1 rules detected fewer supported integrity problems.

It does not prove that a clinical record is medically correct, complete, or safe.

---

## Human Oversight

ClinDrift is designed as a human-centred assurance tool.

When safety-relevant drift is detected, the interface can explicitly display:

> **Human review required**

The prototype does not attempt to replace clinical judgement.

Its role is to make potentially important information changes easier to identify, inspect, and investigate.

---

## Testing

The current automated core test suite covers:

- dosage drift detection
- preservation of an unchanged measurement
- allergy contradiction detection
- duration drift detection

Run the test suite with:

```bash
python -m pytest -v
```

Current v0.1 local test result:

```text
tests/test_core.py::test_detects_dose_drift PASSED
tests/test_core.py::test_preserved_measurement_not_flagged PASSED
tests/test_core.py::test_allergy_contradiction PASSED
tests/test_core.py::test_duration_drift PASSED

4 passed
```

---

## Running ClinDrift Locally

### 1. Clone the repository

```bash
git clone <repository-url>
cd ClinDrift-v0.1
```

The public repository URL will replace `<repository-url>` after the GitHub repository is created.

### 2. Create a virtual environment

On Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the automated tests

```bash
python -m pytest -v
```

### 5. Start ClinDrift

```bash
python -m streamlit run app.py
```

The local application will normally be available at:

```text
http://localhost:8501
```

---

## Research Prototype

ClinDrift is both a software prototype and an experimental research artefact.

The research purpose is to investigate whether clinically important meaning remains intact when health information is transformed.

Potential transformation scenarios include:

- AI-generated clinical notes
- AI-assisted clinical documentation
- clinical summarisation
- GP-to-hospital referrals
- discharge summaries
- patient summaries
- interoperable health records
- cross-system health-information exchange

The prototype focuses on **clinical information integrity**, not diagnosis.

---

## Research Method

ClinDrift v0.1 uses a deliberately transparent pipeline:

1. Extract supported clinical facts from source information.
2. Extract equivalent facts from transformed information.
3. Compare clinically significant values.
4. Identify supported forms of semantic drift.
5. Classify detected findings by severity.
6. Link findings to source and transformed evidence.
7. Calculate an interpretable integrity score.
8. signal when human review is required.
9. Introduce controlled mutations for reproducible testing.
10. Compare injected mutations against detected mutations.

The current prototype favours deterministic and inspectable logic because v0.1 is intended to establish a reproducible baseline before more complex AI-assisted detection approaches are evaluated.

---

## UK Research Context

ClinDrift is relevant to research questions involving:

- AI-assisted clinical documentation
- clinical-information summarisation
- human oversight
- information integrity
- evidence traceability
- privacy and AI security
- clinical-safety monitoring

Future versions may investigate assurance mappings against relevant UK digital-health guidance.

Such mappings would support research and evaluation and would **not constitute a claim of regulatory compliance or certification**.

---

## Canada Research Context

ClinDrift is also relevant to research questions involving:

- AI-scribe deployment
- interoperable patient summaries
- preservation of clinically important information
- validity and reliability of transformed health information
- privacy and security expectations
- human review
- lifecycle assurance

Future research versions may provide a Canadian assurance profile alongside the UK research profile.

---

## Research Roadmap

### v0.2 — Expanded Drift Taxonomy

Planned evaluation includes:

- negation drift
- laterality drift
- medication-frequency drift
- measurement drift
- unsupported additions

### v0.3 — Security Assurance

Planned research exploration includes:

- prompt-injection contamination
- malicious instruction detection
- source-data manipulation
- privacy-leakage indicators

### Research Evaluation

Future benchmarking may evaluate:

- precision
- recall
- F1 score
- critical-error detection rate
- false-positive rate
- mutation detection rate

The roadmap describes planned research and should not be interpreted as functionality already implemented in v0.1.

---

## Limitations

ClinDrift v0.1 is intentionally narrow.

The current prototype does not provide:

- medical diagnosis
- treatment recommendations
- comprehensive clinical NLP
- comprehensive medical terminology coverage
- production-grade EHR integration
- hospital deployment
- medical-device validation
- regulatory certification
- proof that transformed information is clinically correct
- generalisable clinical accuracy claims

The current rule set detects only supported patterns and can miss clinically important changes outside its implemented scope.

False positives and false negatives remain possible.

The prototype therefore requires human verification.

---

## Responsible Use

ClinDrift is a **research and demonstration prototype**.

ClinDrift:

- does not diagnose patients
- does not recommend treatments
- does not replace clinicians
- does not certify AI systems
- does not determine regulatory compliance
- must not be used for clinical decision-making

Human clinical verification remains required.

Synthetic or appropriately de-identified information should be used during research and demonstration.

Do not enter identifiable patient information into public demonstration deployments.

---

## Design Principles

### Transparent

Automated findings should be understandable and inspectable.

### Evidence-based

Supported findings should link back to the information that triggered them.

### Human-centred

Automation should support human review rather than replace it.

### Security-aware

Clinical information integrity is treated as both a patient-safety and cybersecurity concern.

### Reproducible

Controlled mutation testing provides repeatable experiments for evaluating detection behaviour.

---

## Technology

ClinDrift v0.1 is built with:

- Python
- Streamlit
- pandas
- pytest

---

## Project Status

**Version:** v0.1

**Status:** Research Prototype

ClinDrift is under active research and development.

The current release establishes the initial transparent integrity-assurance baseline.

---

## Author

**Blessing Ezeobioha**

Cybersecurity · Artificial Intelligence · Digital Health · Trustworthy Systems

---

## Screenshots

The public repository will include representative screenshots of:

- ClinDrift interface
- source vs transformed clinical information
- Clinical Drift Mutation Lab
- integrity assessment
- evidence traceability
- mutation detection self-test
- audit report
- research prototype interface
- UK and Canada research context

---

## Citation

ClinDrift is currently a v0.1 research prototype.

Formal citation information will be added alongside future research publication and archival releases.

---

## Disclaimer

ClinDrift is provided for research, education, experimentation, and demonstration.

It is not a medical device and is not intended for clinical decision-making.

No output from ClinDrift should be interpreted as medical advice, diagnosis, treatment guidance, regulatory approval, or certification.

Human clinical verification remains required.