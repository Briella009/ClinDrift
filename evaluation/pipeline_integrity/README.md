# ASR-to-note pipeline integrity protocol

## Research question

Can ClinDrift identify or prevent amplification of safety-relevant errors across an ASR-to-generated-note pipeline for Nigerian-accented English and English–Yoruba code-switching?

## Evaluation surfaces

Preserve four aligned surfaces for every case:

1. verified reference transcript;
2. ASR transcript;
3. generated clinical note;
4. ClinDrift findings and reviewer disposition.

The same audio and downstream note-generation configuration should be used for paired comparisons. Freeze model versions, prompts and decoding settings. Repeat stochastic stages so instability is visible.

## Error attribution

Assign each clinically relevant note discrepancy one predeclared root-cause label:

- `note_originated`: absent from the ASR transcript but introduced in the note;
- `propagated_asr`: present in ASR and preserved at comparable severity in the note;
- `amplified_asr`: present in ASR but made more clinically consequential in the note;
- `silently_corrected`: present in ASR but correctly resolved in the note;
- `unresolved`: evidence is insufficient for attribution.

Use two independent qualified annotators and adjudicate disagreements. Keep annotators blind to model identity where feasible.

## Dataset requirements

- Recruit representative speakers with informed consent and local ethics/data-governance approval.
- Report accent, language, code-switch density, recording device, acoustic environment and consultation complexity without treating accent as a deficit.
- Include multiple speakers and scripts in every stratum; do not confound one script with one complexity level.
- Store raw audio only under explicit retention and access controls. Publish derived or synthetic artifacts when raw data cannot be shared.

## Metrics

- ASR word error rate as a contextual metric, not the safety endpoint;
- clinically weighted ASR error rate;
- serious note-error rate;
- propagation, amplification and silent-correction rates;
- ClinDrift Critical recall and catastrophic-miss rate;
- false-positive rate on clean/meaning-preserving cases;
- review burden and review time;
- repeated-run stability;
- all safety metrics by language/accent group with uncertainty intervals and sample counts.

Predeclare a minimum acceptable Critical recall and maximum review burden before opening the held-out labels. Report worst-group results alongside pooled results.

## Scope boundary

This protocol is prospective. ClinDrift does not currently ingest audio, and no claim of performance for Nigerian-accented English or English–Yoruba code-switching should be made until the governed dataset and independent evaluation are complete.
