# ClinDrift presentation walkthrough

This walkthrough is for a safe live demonstration of the current deterministic ClinDrift research prototype.

## Public demo boundary

Use only synthetic, redacted, or explicitly authorised non-confidential text in the public Streamlit deployment. ClinDrift is not a diagnostic system and its output requires human clinical verification.

## Recommended 3-minute demonstration

1. Open the ClinDrift app and select **Home**.
2. Select **Load drift example** on Home. This only prepares synthetic source and transformed records; it does not run an analysis.
3. Open **Mutation Lab** to show the deliberately injected dosage, allergy, and duration changes.
4. Open **Integrity Check**, select **Run integrity check**, then show:
   - integrity score;
   - number of findings;
   - critical findings;
   - risk level;
   - controlled self-test results.
5. Open **Evidence** and expand each finding to show the source text, transformed text, and the reason it was flagged.
6. On **Evidence**, enter a reviewer note, select **Save reviewer note**, and confirm that the note is saved for the current session.
7. Open **Audit Report** and confirm the reviewer note is displayed. Download both PDF and JSON reports, and verify the same note and findings appear in each. You can also preview the JSON report.

## What is implemented now

- Real sidebar navigation between Home, Mutation Lab, Integrity Check, Evidence, and Audit Report.
- Explicit two-step workflow: **Load drift example** prepares the records; **Run integrity check** generates findings only after the click.
- Working sample/reset/clear controls.
- Working controlled-mutation generation; no automatic analysis or stale mutation results after manual edits.
- Working integrity analysis and evidence views.
- Working PDF and JSON report downloads.
- Explicit **Save reviewer note** action; unsaved drafts cannot silently replace the saved note in PDF or JSON exports.
- Vertical, mobile-friendly cards for findings, evidence, controlled mutations, and self-test results.

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
