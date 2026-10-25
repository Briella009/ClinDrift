# Evidence Pairing Baseline

The semantic pipeline separates **evidence retrieval** from **NLI classification**.

## Why the separation matters

A correct NLI classifier can still fail end to end if it is given the wrong
source sentence. ClinDrift therefore evaluates:

1. **oracle-pair inference** - the NLI model receives the known relevant pair;
2. **automatic-pair inference** - an evidence retriever selects candidates
   before NLI.

The difference between these results helps identify whether an error came from
retrieval or inference.

## Current baseline

`src/evidence_pairing.py` implements a transparent RapidFuzz token-set
baseline. It is intentionally simple and reproducible.

It performs both:

- transformed -> source retrieval for support, contradiction, and possible
  unsupported additions;
- source -> transformed retrieval for preservation and possible omissions.

The lexical method is a **baseline**, not a claim that lexical similarity is
sufficient for clinical semantic retrieval. A later development-only
experiment may compare it with an embedding-based retriever if the added
complexity is justified.

## Metric

Pairing recall@k is reported against gold evidence-pair indices before NLI
performance is interpreted. Final reporting should distinguish:

- oracle-pair NLI metrics;
- automatic-pair end-to-end metrics;
- pairing recall@k.

No retrieval metric is a clinical-validation claim.
