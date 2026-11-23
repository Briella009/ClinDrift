# Defense demonstration checklist

ClinDrift is a research prototype for selected forms of clinical-text drift. Use the built-in synthetic demo, not patient records.

1. Open the deployed Streamlit app; check that the Home page and five-page navigation appear.
2. On **Home**, select **Prepare presentation demo**. Alternatively, use **Prepare full demo case** in the sidebar.
3. Open **Mutation Lab**; show the injected changes and the changed text.
4. Open **Integrity Check**, then select **Run integrity check**. Explain the integrity score, findings, severity and controlled self-test.
5. Open **Evidence**; expand at least one finding. Point out source evidence, transformed evidence and rationale.
6. In **Reviewer note**, enter: "Clinician review required: verify the metformin dosage before approval." Select **Save reviewer note** and confirm the success message.
7. Open **Audit Report**. Read the same reviewer note displayed on-screen.
8. Select **Download PDF report**. Open the PDF and show the finding, evidence and review note.
9. Select **Download JSON report**. Inspect the \`review_note\`, \`integrity_score\`, \`findings\` and \`controlled_mutations\` values. They must describe the same analysis.
10. Return to **Evidence**; the note should remain in this session. Use **Clear inputs**, **Load clean sample**, and **Generate controlled drift** only after the main presentation, because a new case resets the previous report and note.

## Before the defense

- Open the deployed app in your defense browser at least once; wake it if asleep.
- Trial both downloads and open them on the presentation computer.
- Keep a sample PDF and JSON downloaded locally as backups in case of Wi-Fi or cloud downtime.
- Avoid browser refresh or session changes after saving the reviewer note; Streamlit's in-memory session is not persistent storage.

## Limitations to state accurately

The current online app is a deterministic research baseline. It checks supported patterns in synthetic clinical information. It is not a validated diagnostic tool, does not provide generalisable accuracy guarantees and requires human clinical verification.
