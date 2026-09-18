# ClinDrift presentation walkthrough

This walkthrough is for a safe live demonstration of the current deterministic ClinDrift research prototype.

## Public demo boundary

Use only synthetic, redacted, or explicitly authorised non-confidential text in the public Streamlit deployment. ClinDrift is not a diagnostic system and its output requires human clinical verification.

## Recommended 3-minute demonstration

1. Open the ClinDrift app and select **Home**.
2. Select **Prepare presentation demo** or use **Prepare full demo case** in the sidebar.
3. Open **Mutation Lab** to show the deliberately injected dosage, allergy, and duration changes.
4. Open **Integrity Check** and show:
   - integrity score;
   - number of findings;
   - critical findings;
   - risk level;
   - controlled self-test results.
5. Open **Evidence** and expand each finding to show the source text, transformed text, and the reason it was flagged.
6. Add an optional reviewer note to demonstrate human-in-the-loop review.
7. Open **Audit Report** and download or preview the JSON report.

## What is implemented now

- Real sidebar navigation between Home, Mutation Lab, Integrity Check, Evidence, and Audit Report.
- Safe presentation shortcut that loads a synthetic case, injects controlled drift, and runs the detector.
- Working sample/reset/clear controls.
- Working controlled-mutation generation.
- Working integrity analysis and evidence views.
- Working JSON report download.
- Optional reviewer note retained in the demonstration report.

## What is intentionally not claimed

The current public prototype is a deterministic baseline. The master's project will evaluate an explainable AI semantic-verification layer against this baseline. The current demo must not be described as a clinically validated AI diagnostic system.

## Local Docker run

```bash
docker compose up --build
```

Then open:

```text
http://localhost:8501
```

Stop with:

```bash
docker compose down
```
