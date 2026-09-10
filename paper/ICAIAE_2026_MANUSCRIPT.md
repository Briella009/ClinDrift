# ClinDrift: An Evidence-Traceable Approach to Detecting Safety-Relevant Semantic Drift in AI-Transformed Clinical Text

**Author:** Blessing Ezeobioha  
**Target venue:** International Conference on Artificial Intelligence Applications and Emerging Analytics (ICAIAE 2026)  
**Track:** AI in Healthcare and Life Sciences  
**Status:** Working manuscript draft

## Abstract

Generative artificial intelligence is increasingly used to summarise, restructure and generate clinical documentation. A transformed note may remain fluent and plausible while changing, omitting or introducing clinically important information. This paper presents ClinDrift, an open-source research prototype that provides an evidence-traceable assurance layer for comparing source clinical information with AI-transformed text. The system uses deterministic fact extraction, restricted canonicalisation, value comparison, severity assignment, integrity scoring and claim-level evidence linking. We evaluated the approach using a 140-case synthetic controlled benchmark containing 100 deliberately altered cases and 40 meaning-preserving controls. Eighty positive cases fell within the implemented fact taxonomy, covering medication dosage, allergy status, duration, medication frequency, blood-pressure measurements, laterality, omissions and supported transformed-only additions. Twenty challenge cases represented unsupported diagnoses and general semantic contradictions outside the implemented ontology. On the current evaluation branch, ClinDrift produced 80 true positives, 40 true negatives, no false positives and 20 false negatives, corresponding to precision 1.000, recall 0.800, F1 0.889, specificity 1.000 and accuracy 0.857 at case level. All 80 in-taxonomy positive cases were flagged, while none of the 20 out-of-taxonomy challenge cases were detected. A restricted normalisation layer reduced false positives on duration and frequency paraphrase controls and improved accuracy on the same benchmark from 0.679 to 0.857 compared with reconstructed v0.1 baseline logic. These results do not establish clinical validity; the benchmark is synthetic and partly informed by previously observed failure modes. Instead, the study demonstrates the value and limits of transparent fact-level assurance and motivates a hybrid architecture in which deterministic verification is complemented by semantic reasoning while preserving evidence traceability and human oversight.

**Keywords:** clinical AI; generative AI; clinical documentation; semantic drift; information integrity; evidence traceability; patient safety; human oversight

## 1. Introduction

Generative artificial intelligence is moving rapidly into healthcare documentation workflows. Large language models can summarise encounters, restructure information, draft clinical notes and support ambient documentation. These applications may reduce administrative burden, but they also create a distinct assurance problem: the transformed text can be linguistically convincing even when clinically important information has changed. A medication dose can be altered, an allergy can be contradicted, a measurement can be replaced, or a clinically relevant statement can disappear while the resulting document remains coherent.

This problem is not adequately captured by fluency or surface similarity alone. In clinical settings, a transformation is trustworthy only if clinically important meaning remains faithful to the source. Recent work on medical summarisation therefore increasingly evaluates factuality, omissions and unsupported content rather than relying exclusively on lexical overlap. MED-OMIT, for example, treats omission as a clinically consequential evaluation target and assesses which missing facts matter to downstream clinical reasoning [1]. More broadly, emerging work on medical language-model evaluation reflects concern that plausible outputs can still contain unsupported or clinically consequential errors.

The governance implications are equally important. The World Health Organization has repeatedly emphasised that AI for health should be designed and deployed with safety, accountability, transparency and human oversight in mind [2,3]. For clinical documentation, this suggests that assurance tools should not merely assign a global quality score. They should make it possible for a reviewer to see what changed, why it was flagged and which source and transformed text spans support the finding.

ClinDrift was created to explore that narrower problem. It is not a diagnostic model, clinical decision-support system or general-purpose factuality evaluator. It is a deterministic research prototype designed to answer a more specific question: did selected clinically important facts survive transformation from a source record into AI-generated or otherwise transformed clinical text?

The prototype extracts supported fact categories from both texts, compares values, assigns severity to detected discrepancies, calculates an interpretable integrity score and links each finding to evidence on both sides. A controlled Mutation Lab allows known changes to be introduced deliberately so that detector behaviour can be tested reproducibly. An initial 12-scenario baseline evaluation exposed both successful detections and important weaknesses, particularly false positives on equivalent paraphrases and false negatives for unsupported additions and broader semantic contradictions. Rather than concealing those weaknesses, the present study uses them to construct an expanded controlled evaluation and to test a restricted canonicalisation improvement.

This paper makes four contributions. First, it presents an inspectable fact-level clinical-information assurance pipeline in which every supported finding retains source and transformed evidence. Second, it introduces an expanded 140-case controlled benchmark that tests both supported detector categories and deliberately out-of-scope semantic challenges. Third, it evaluates a restricted normalisation layer intended to reduce false positives caused by equivalent duration and medication-frequency expressions. Fourth, it reports explicit failure boundaries, showing that good performance inside a narrow implemented taxonomy must not be confused with general clinical semantic verification.

The central claim is therefore deliberately limited: transparent deterministic assurance can be useful for selected, high-value clinical facts, but it should be treated as a component of a broader human-centred assurance architecture rather than as proof that AI-transformed clinical text is correct or safe.

## 2. Related Work

### 2.1 Factuality and omission in clinical summarisation

Clinical summarisation differs from general summarisation because a small factual change may have disproportionate consequences. A fluent summary that omits an important medication, reverses a negation or changes a measurement can misrepresent a patient's state. Schumacher et al. introduced MED-OMIT to evaluate clinically important omissions by decomposing medical dialogue into facts and estimating the clinical relevance of omitted information [1]. Their work highlights a central point for this study: evaluation should operate at the level of clinically meaningful facts rather than only document-level resemblance.

Related research increasingly treats medical factuality as a fine-grained verification problem. This direction is important because conventional overlap-based measures may reward wording similarity without demonstrating that clinically significant assertions remain supported. ClinDrift is aligned with this fact-level perspective but differs in its emphasis on transparent, deterministic comparison and explicit evidence links rather than on an end-to-end learned evaluator.

### 2.2 Hallucination and unsupported clinical content

Generative models can introduce information that is absent from the source, a failure mode commonly described as hallucination or unsupported generation. In clinical documentation, unsupported additions are especially concerning because they may appear plausible to a human reader. ClinDrift distinguishes between supported transformed-only additions that fall within its implemented extraction categories and arbitrary unsupported clinical assertions that the current ontology does not capture.

This distinction is methodologically important. A system should not be credited with detecting unsupported content merely because it identifies one narrow class of transformed-only facts. The present evaluation therefore includes dedicated unsupported-diagnosis challenge cases designed to fail under the current extraction scope. Reporting those failures is necessary to avoid overstating capability.

### 2.3 Evidence-grounded and process-level assurance

Recent medical-AI research has also shifted toward evidence-aware evaluation. Med-PRM, for example, evaluates intermediate reasoning steps against retrieved medical evidence, illustrating the value of localising errors rather than relying solely on final-answer correctness [4]. Although ClinDrift addresses a different task, the design principle is similar: an automated finding should be inspectable and connected to the evidence that produced it.

ClinDrift therefore stores the drift type, severity, source value, transformed value, source evidence, transformed evidence and a human-readable rationale. This supports reviewability and helps separate the detection mechanism from the reviewer who ultimately decides whether a change is clinically meaningful.

### 2.4 Governance and human oversight

WHO guidance on AI for health emphasises ethical deployment, accountability and the protection of human autonomy [2]. Its later guidance on large multi-modal models further recognises the opportunities and risks associated with generative AI in healthcare [3]. These principles support a human-in-the-loop interpretation of ClinDrift. The system is designed to surface discrepancies for review, not to determine whether a clinical record is medically correct, approve an AI system, or replace professional judgement.

## 3. ClinDrift Design

### 3.1 System objective

ClinDrift compares two text inputs: a source clinical record and a transformed record. The transformed text may represent an AI-generated note, summary, rewrite or other text transformation. The system asks whether selected supported facts are preserved between the two representations.

The processing pipeline contains six stages:

1. clinical fact extraction from the source record;
2. clinical fact extraction from the transformed record;
3. restricted normalisation of selected equivalent surface forms;
4. fact comparison and drift classification;
5. severity assignment and integrity scoring; and
6. claim-level evidence presentation and human-review signalling.

The implementation is intentionally deterministic. This choice makes the current behaviour inspectable and reproducible and provides a baseline against which future semantic or model-based approaches can be compared.

### 3.2 Supported fact taxonomy

The current extractor recognises a deliberately limited set of information categories. These include medication names from a finite medication hint list, medication dosages, blood-pressure-style measurements, durations, medication frequencies, laterality terms, selected allergy statements and selected negation patterns.

Direct comparison is used for dosage, duration, frequency, laterality and measurement when a single supported value exists on each side. Allergy-specific rules identify transformations between a documented allergy and a statement indicating no known allergies. More general source-only facts can be surfaced as omission candidates, while transformed-only supported facts can be surfaced as unsupported additions.

The narrow taxonomy is a design constraint rather than an accidental omission. The prototype does not claim comprehensive clinical natural-language understanding.

### 3.3 Restricted canonicalisation

The v0.1 baseline evaluation showed that clinically equivalent expressions could generate false positives. Examples included `3 days` versus `three days` and `twice a day` versus `twice daily`. The current evaluation branch introduces restricted canonicalisation for these known expression families.

Number words from one through twelve are normalised to digits for duration expressions. Frequency expressions are mapped to a smaller set of canonical forms, including mappings such as `daily` and `once per day` to `once a day`, `twice daily` to `twice a day`, and `once a week` to `weekly`.

This layer is intentionally small and explicit. It should not be interpreted as general semantic equivalence detection.

### 3.4 Drift findings and evidence traceability

Each supported finding records a drift type, severity, source value, transformed value, source evidence, transformed evidence and rationale. The purpose is to prevent a reviewer from receiving an unexplained alert detached from the text that triggered it.

For example, if `metformin 500 mg` becomes `metformin 1000 mg`, the finding can show both dosage values and the source sentences from which they were extracted. This creates an auditable path from system output back to the underlying text.

### 3.5 Severity and integrity scoring

The prototype assigns category-based severity levels. Allergy, dosage, measurement and selected negation findings are treated as Critical; medication, frequency, laterality and duration findings are treated as High. Other findings default to Medium. The integrity score starts at 100 and subtracts fixed penalties according to finding severity.

This score is an engineering signal for the prototype interface, not a validated measure of clinical risk. A score of 100 means only that the implemented rules did not detect a supported discrepancy. It does not prove that the transformed note is complete, accurate or clinically safe.

## 4. Methods

### 4.1 Study design

We conducted a controlled synthetic evaluation of ClinDrift. The objective was not to estimate real-world clinical accuracy. Instead, the benchmark was designed to characterise detector behaviour under known transformations and explicit boundary conditions.

The study builds on an earlier 12-scenario baseline evaluation that had already revealed several strengths and failure modes. Consequently, the 140-case benchmark should be understood as an expanded functional stress test rather than an independent external holdout set. This distinction is important because some test categories were chosen specifically to reproduce known weaknesses.

### 4.2 Benchmark construction

The benchmark contains 140 paired source/transformed examples. One hundred are positive cases containing a deliberately introduced information-integrity change and 40 are negative controls intended to preserve meaning.

The positive set contains ten cases in each of ten groups: dosage drift, allergy contradiction, duration drift, frequency drift, blood-pressure measurement drift, laterality drift, omission, supported transformed-only fact addition, unsupported diagnosis addition and general semantic contradiction.

The negative-control set contains ten unchanged cases, ten formatting-equivalent cases, ten duration-paraphrase cases and ten frequency-paraphrase cases.

The first eight positive categories, representing 80 cases, are substantially aligned with the implemented extraction and comparison taxonomy. The remaining 20 positive cases intentionally require information types or semantic reasoning that the current detector does not implement. This structure allows the evaluation to distinguish in-scope functional performance from out-of-scope challenge behaviour.

No identifiable patient data were used. Examples were synthetic and constructed for research evaluation.

### 4.3 Ground truth

Each case was labelled as positive or negative independently of detector output. Positive cases contain an intentionally introduced change in clinical meaning or support; negative controls preserve the intended meaning despite possible formatting or wording changes.

For the primary case-level analysis, a positive case was counted as detected when ClinDrift returned at least one finding. A negative case was counted as correctly handled when no finding was returned. This metric therefore evaluates case-level alerting rather than exact span-level or drift-type classification accuracy.

### 4.4 Experimental conditions

Two detector configurations were compared on the same 140 cases.

The first reconstructs the pre-normalisation v0.1 extraction behaviour from the main-branch implementation. The second uses the ICAIAE evaluation branch, which adds restricted duration and frequency canonicalisation and expanded recognition of equivalent frequency expressions while leaving the broader deterministic architecture unchanged.

Using the same cases for both configurations provides a paired comparison of the targeted change. However, because the benchmark was informed by known v0.1 errors, the comparison must not be interpreted as external validation.

### 4.5 Evaluation metrics

At case level we calculated true positives (TP), true negatives (TN), false positives (FP) and false negatives (FN). From these counts we calculated:

- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- F1 = 2 × Precision × Recall / (Precision + Recall)
- Specificity = TN / (TN + FP)
- Accuracy = (TP + TN) / N

We also report group-level detection counts to show where overall metrics are being gained or lost. For the paired comparison, we examined cases whose correctness changed between configurations and applied an exact McNemar test to the discordant pairs.

## 5. Results

### 5.1 Overall performance

On the 140-case benchmark, the current ICAIAE branch produced 80 true positives, 40 true negatives, no false positives and 20 false negatives. This corresponds to precision 1.000, recall 0.800, F1 0.889, specificity 1.000 and accuracy 0.857.

All 80 positive cases within the implemented fact taxonomy produced at least one alert. The 20 false negatives came entirely from the two deliberately out-of-scope challenge groups: unsupported diagnoses and general semantic contradictions.

| Metric | Current branch |
|---|---:|
| Cases | 140 |
| True positives | 80 |
| True negatives | 40 |
| False positives | 0 |
| False negatives | 20 |
| Precision | 1.000 |
| Recall | 0.800 |
| F1 | 0.889 |
| Specificity | 1.000 |
| Accuracy | 0.857 |

### 5.2 Detection by category

The current branch flagged all ten cases in each of the eight supported positive groups: dosage, allergy contradiction, duration, frequency, measurement, laterality, omission and supported transformed-only additions. The 30 cases in the supported dosage, allergy and blood-pressure measurement groups, which are classified as Critical by the prototype severity rules, were all flagged at case level.

By contrast, none of the ten unsupported-diagnosis cases and none of the ten general semantic-contradiction cases produced a finding. Examples include transformations such as `The patient is afebrile` to `The patient is febrile` and the addition of a diagnosis such as chronic kidney disease when the source contained no such assertion. These examples do not match the current deterministic fact ontology.

This produces a useful separation in the results: performance is strong on deliberately represented fact categories but collapses on semantic phenomena outside the rule set.

### 5.3 Negative controls

The current branch generated no false positives across the 40 negative controls. This includes unchanged text, formatting-equivalent text, duration paraphrases and frequency paraphrases represented in the benchmark.

The absence of false positives should be interpreted narrowly. These controls were synthetic and cover a restricted collection of known equivalences. The result does not establish that ClinDrift will avoid false positives across unrestricted clinical paraphrasing.

### 5.4 Effect of restricted canonicalisation

The same benchmark was executed against reconstructed pre-normalisation v0.1 logic. Under that configuration, performance was TP=79, TN=16, FP=24 and FN=21, corresponding to precision 0.767, recall 0.790, F1 0.778, specificity 0.400 and accuracy 0.679.

After restricted normalisation, false positives fell from 24 to 0, true negatives increased from 16 to 40, and one additional frequency-drift case became detectable. Accuracy increased from 0.679 to 0.857 and F1 from 0.778 to 0.889.

| Metric | v0.1 baseline logic | Current branch |
|---|---:|---:|
| Precision | 0.767 | 1.000 |
| Recall | 0.790 | 0.800 |
| F1 | 0.778 | 0.889 |
| Specificity | 0.400 | 1.000 |
| Accuracy | 0.679 | 0.857 |

At the paired case-correctness level, 25 cases changed from incorrect under the earlier logic to correct under the current branch, while no cases changed from correct to incorrect. An exact McNemar test on the discordant cases yielded p < 0.001.

This result supports the targeted engineering change on this benchmark. It does not establish general superiority on external clinical text because the benchmark itself was partly designed around known baseline failure modes.

## 6. Discussion

The results demonstrate both the usefulness and the limitations of a deterministic clinical-information assurance layer. Within the implemented fact taxonomy, ClinDrift reliably surfaced the controlled changes used in this study. This suggests that narrow, transparent rules can be valuable when the assurance target is explicit and high value, such as medication dose, allergy contradiction, blood-pressure measurement or laterality.

The evidence-traceable design is also important. A detector that simply returns `unsafe` or a probability score provides limited assistance to a reviewer. ClinDrift instead links findings to the corresponding source and transformed evidence. This makes the output inspectable and supports a human-in-the-loop workflow consistent with broader calls for transparency and oversight in medical AI [2,3].

The normalisation experiment shows a second practical lesson. Some apparent semantic errors are representation problems rather than reasoning problems. Mapping a small set of equivalent duration and frequency expressions eliminated the false positives represented in the controlled paraphrase groups. Because the mapping is explicit, reviewers can understand exactly which equivalences are being assumed.

However, the 20 false negatives reveal the central limitation of the present approach. ClinDrift cannot detect arbitrary unsupported diagnoses or contradictions expressed outside its encoded categories. A statement may therefore change from afebrile to febrile, or a new diagnosis may be invented, without triggering the current detector. These are not minor edge cases. They represent precisely the kinds of failures that make unrestricted generative clinical documentation difficult to assure.

For that reason, the most promising future architecture is not to replace the deterministic layer with an opaque model, but to combine complementary mechanisms. Structured-value checks can remain deterministic where possible. A semantic verifier can then inspect relations, negation, diagnoses and unsupported assertions that fall outside the rule set. Crucially, any model-based layer should preserve the evidence-traceability principle by attaching a proposed discrepancy to explicit source and transformed spans and by allowing human reviewers to reject uncertain findings.

The evaluation also highlights the difference between benchmark performance and clinical validity. An F1 score of 0.889 on this experiment does not mean that ClinDrift is 88.9% clinically accurate. The benchmark is synthetic, small relative to the diversity of clinical language, and partly aligned to implemented rules. The strong in-taxonomy result should therefore be read as a functional verification result: given these explicitly represented controlled changes, the system behaved as designed.

## 7. Limitations

This study has several limitations. First, the benchmark contains synthetic records rather than independently sourced clinical notes. This protects patient privacy and supports exact ground truth, but it limits linguistic and clinical realism.

Second, benchmark design was informed by an earlier 12-scenario evaluation. The current evaluation is therefore not a fully independent holdout test. The improvement produced by canonicalisation is meaningful for regression testing but may overestimate the reduction in false positives that would be observed on new clinical language.

Third, the positive set contains many cases aligned with the current rule taxonomy. Eighty of the 100 positive cases test supported categories, while only 20 deliberately probe unsupported semantic phenomena. Overall precision, recall and F1 therefore depend strongly on this benchmark composition.

Fourth, the primary outcome is case-level alerting. The study does not yet provide span-level precision, exact drift-type classification metrics, calibration measures, clinician-rated severity agreement or estimates of downstream clinical impact.

Fifth, the medication vocabulary, extraction patterns and severity scheme are deliberately limited. The prototype does not provide comprehensive terminology coverage, EHR integration, medical-device validation or regulatory certification.

Finally, the study does not compare ClinDrift against contemporary LLM-based factuality evaluators on the same dataset. Such comparison would be important in future work to determine whether a hybrid approach improves semantic coverage without sacrificing interpretability or introducing unacceptable false positives.

## 8. Future Work

The next phase should evaluate ClinDrift on an independently constructed benchmark that was not used to guide detector changes. Where governance and ethics approvals permit, this should include de-identified or publicly available clinical text and clinician annotation.

A second priority is semantic coverage. Unsupported diagnoses, assertion status, general negation and relational contradictions require capabilities beyond the current rule set. A hybrid verifier could combine deterministic checks with a constrained semantic model or natural-language inference layer.

Third, future evaluation should move beyond case-level detection to include exact finding-level precision and recall, evidence-span correctness, severity agreement, reviewer workload and time-to-verification. These measures would better assess whether the tool actually helps clinicians or safety reviewers.

Finally, robustness testing should include adversarial paraphrases, abbreviation variation, spelling errors, multiple medications, multiple measurements, conflicting temporal references and longer clinical documents.

## 9. Conclusion

ClinDrift demonstrates that a narrow, evidence-traceable deterministic layer can detect selected safety-relevant information changes in AI-transformed clinical text while exposing its own limits. On a 140-case synthetic controlled benchmark, the current evaluation branch achieved precision 1.000, recall 0.800, F1 0.889, specificity 1.000 and accuracy 0.857 at case level. All supported-category cases were flagged, while unsupported diagnoses and general semantic contradictions remained undetected.

The most important result is therefore not the aggregate score. It is the boundary it reveals. Explicit structured facts can be checked transparently and reproducibly, but unrestricted clinical meaning cannot be assured by a narrow deterministic ontology. A practical future assurance architecture should combine deterministic checks, evidence-grounded semantic verification and human review. ClinDrift provides an open baseline for investigating that combination without treating fluent AI-generated documentation as inherently trustworthy.

## Responsible-use statement

ClinDrift is a research and demonstration prototype. It is not a medical device, does not diagnose patients, does not recommend treatment, does not certify AI systems and must not be used as a substitute for clinical verification. The present study used synthetic text and makes no claim of clinical validation.

## References

[1] E. Schumacher, D. Rosenthal, D. Naik, V. Nair, L. Price, G. Tso, and A. Kannan, "Extrinsically-Focused Evaluation of Omissions in Medical Summarization," arXiv:2311.08303, 2023.

[2] World Health Organization, *Ethics and Governance of Artificial Intelligence for Health: WHO Guidance*. Geneva: WHO, 2021. ISBN 978-92-4-002920-0.

[3] World Health Organization, *Ethics and Governance of Artificial Intelligence for Health: Guidance on Large Multi-Modal Models*. Geneva: WHO, 2024/2025. ISBN 978-92-4-008475-9.

[4] J. Yun et al., "Med-PRM: Medical Reasoning Models with Stepwise, Guideline-verified Process Rewards," arXiv:2506.11474, 2025.

> **Reference-development note:** The final submission should expand the literature review and bibliography with peer-reviewed work on clinical note generation, factual consistency, ambient AI documentation, clinical hallucination evaluation and fact-level EHR verification. References must be checked against the final ICAIAE citation style before submission.
