# September 2026 research integration

This note converts recent clinical-AI safety evidence into testable ClinDrift work. It is a research roadmap, not a claim that the prototype is clinically safe or deployment-ready.

## Implemented in this branch

| Evidence-driven recommendation | ClinDrift change | Evidence to collect next |
| --- | --- | --- |
| Do not treat the phrase “human review” as a sufficient safeguard | Each finding now carries a stable review ID, exact evidence, a category-specific verification question, a required action, an escalation rule and a constrained reviewer disposition. These fields are exported in the audit report. | Compare unaided review with ClinDrift-supported review using detection sensitivity, false-alert burden, time and between-reviewer variation. |
| Report catastrophic failures rather than only aggregate accuracy | `src/safety_metrics.py` provides critical-error recall and catastrophic-miss rate. | Predeclare which benchmark errors count as Critical, freeze labels and report confidence intervals. |
| Test reproducibility rather than assuming deterministic behaviour from one run | `repeated_run_stability` measures mean pairwise agreement across finding sets. | Run every stochastic NLI configuration repeatedly with fixed and varied seeds; report both label and evidence-pair stability. |
| Make the review burden visible | `review_burden` reports the share of cases escalated. | Report burden by category, severity, language/accent group and operating threshold. |
| Evaluate the complete documentation pipeline | A pipeline-integrity protocol and machine-readable case schema now separate reference, ASR, generated-note and ClinDrift-review stages. | Attribute each serious note error as note-originated, propagated from ASR, amplified from ASR, silently corrected or unresolved. |

## Trustworthiness coverage

The dimensions below adapt the MedGuard framing to ClinDrift's narrower documentation-integrity task. Passing one dimension must not be presented as proof of overall trustworthiness.

| Dimension | ClinDrift control or planned test | Minimum reportable evidence | Current gap |
| --- | --- | --- | --- |
| Truthfulness | Bidirectional source-to-note and note-to-source checks | Critical-error recall, false-positive rate and evidence-pair recall | Held-out clinical evaluation is not complete |
| Resilience | Controlled mutations, acoustic stress and rule–AI discordance handling | Performance by mutation/noise type and worst-group result | No adversarial red-team suite yet |
| Fairness | Planned subgroup evaluation for Nigerian-accented English and English–Yoruba code-switching | Sample counts, subgroup uncertainty intervals and worst-group critical recall | Representative, consented speech data are not yet available |
| Robustness | Repeated-run stability and out-of-template held-out cases | Pairwise stability, calibration and external/site shift results | No external-site validation |
| Privacy | Local inference target, no external generative API requirement and synthetic/redacted demo policy | Data-flow diagram, retention controls, dependency and threat review | No formal privacy threat model or penetration test |

## Evidence informing the changes

- [A multicenter assessment of human oversight of generative AI outputs in simulated clinical decision making](https://www.nature.com/articles/s41746-026-03294-x) (peer reviewed, 24 September 2026) motivates testing the reviewer workflow rather than assuming that clinician presence catches errors.
- [Development of a Framework for Evaluating Large Language Model Safety and Reliability](https://link.springer.com/article/10.1007/s10916-026-02459-1) (peer reviewed, 23 September 2026) motivates catastrophic-failure and repeated-run reporting.
- [Assessing safety and trustworthiness of large language models in medicine](https://www.nature.com/articles/s43856-026-01881-3) (peer reviewed, 19 September 2026) supplies the multidimensional trustworthiness framing associated with MedGuard.
- [Mind the gap: emergent clinical risk at the interface of two individually safe AI systems in a multilingual ambient scribe](https://www.medrxiv.org/content/10.64898/2026.09.22.26363642v1) (preprint, 22 September 2026) motivates stage-level root-cause attribution. Its findings should be treated as provisional until peer review and independent replication.
- [Human in the loop in AI-enabled clinical decision support](https://pubmed.ncbi.nlm.nih.gov/42731360/) (peer reviewed, 10 September 2026) motivates lifecycle reporting of who reviews what, when and with which authority.

## Interpretation boundary

The new review prompts are an intervention to evaluate. They must not be described as proven mitigation. The new metrics expose failure patterns but do not themselves improve clinical performance. Any paper or demonstration should report the prototype status, synthetic-development-data boundary, unresolved fairness/privacy work and need for prospective clinical validation.
