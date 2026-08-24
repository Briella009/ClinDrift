import json

import pandas as pd
import streamlit as st

from src.extractor import extract_facts
from src.drift_engine import compare_facts
from src.scoring import integrity_score, review_status
from src.mutations import apply_all_mutations


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="ClinDrift",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# BRAND / UI CSS
# =========================================================

st.markdown(
    """
<style>
.stApp {
    background:
        radial-gradient(circle at 85% 5%, rgba(109,23,56,0.18), transparent 30%),
        radial-gradient(circle at 15% 80%, rgba(166,61,99,0.08), transparent 28%),
        #0E1117;
    color: #F5F3F4;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 1500px;
}

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #351020 0%,
            #210D17 52%,
            #100A0E 100%
        );
    border-right: 1px solid rgba(196,101,131,0.30);
}

[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

h1, h2, h3 {
    letter-spacing: -0.02em;
}

p {
    line-height: 1.55;
}

hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(196,101,131,0.75),
        transparent
    ) !important;
    margin: 2rem 0 !important;
}

div.stButton > button {
    border-radius: 10px;
    border: 1px solid #A63D63;
    font-weight: 700;
    min-height: 46px;
    transition: 0.2s ease;
}

div.stButton > button:hover {
    border-color: #D15A84;
    box-shadow: 0 0 0 2px rgba(166,61,99,0.18);
    transform: translateY(-1px);
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(
        135deg,
        #861A47,
        #C52F68
    );
    color: white;
    border: 1px solid #E15B88;
}

div.stDownloadButton > button {
    width: 100%;
    border-radius: 10px;
    border: 1px solid #A63D63;
    color: #F5F3F4;
    min-height: 46px;
    font-weight: 700;
}

textarea {
    border: 1px solid rgba(196,101,131,0.55) !important;
    border-radius: 12px !important;
    background-color: #171B22 !important;
    color: #F5F3F4 !important;
}

textarea:focus {
    border-color: #D15A84 !important;
    box-shadow: 0 0 0 1px #D15A84 !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid rgba(196,101,131,0.28);
    border-radius: 12px;
    overflow: hidden;
}

[data-testid="stExpander"] {
    border: 1px solid rgba(196,101,131,0.28);
    border-radius: 12px;
    background: rgba(23,27,34,0.78);
    overflow: hidden;
}

[data-testid="stMetric"] {
    background:
        linear-gradient(
            145deg,
            rgba(29,34,43,0.97),
            rgba(17,20,27,0.97)
        );
    border: 1px solid rgba(196,101,131,0.27);
    border-radius: 14px;
    padding: 1rem;
    min-height: 125px;
}

[data-testid="stMetricValue"] {
    color: #F5F3F4;
    font-weight: 800;
}

[data-testid="stMetricLabel"] {
    color: #C9C3C6;
}

[data-testid="stAlert"] {
    border-radius: 12px;
}

.brand-header {
    padding: 1.15rem 1.25rem 1.25rem 1.25rem;
    margin-bottom: 1rem;
    background:
        linear-gradient(
            120deg,
            rgba(109,23,56,0.28),
            rgba(14,17,23,0.30)
        );
    border: 1px solid rgba(196,101,131,0.30);
    border-radius: 18px;
}

.brand-row {
    display: flex;
    align-items: center;
    gap: 16px;
}

.logo-mark {
    width: 62px;
    height: 62px;
    border-radius: 18px;
    border: 1px solid rgba(209,90,132,0.72);
    display: flex;
    align-items: center;
    justify-content: center;
    background:
        radial-gradient(
            circle,
            #F4D7E1 0%,
            #E66691 16%,
            #8B1E4B 38%,
            #310D1C 68%,
            #171018 100%
        );
    box-shadow:
        0 0 24px rgba(182,43,97,0.26);
    flex-shrink: 0;
}

.logo-mark-inner {
    width: 17px;
    height: 17px;
    background: #F5F3F4;
    border-radius: 50%;
    box-shadow:
        0 0 0 7px rgba(230,102,145,0.22),
        0 0 0 14px rgba(230,102,145,0.08);
}

.brand-title {
    font-size: 2.65rem;
    line-height: 1;
    font-weight: 800;
    margin: 0;
    color: #F5F3F4;
}

.brand-title span {
    color: #D94B7A;
}

.brand-subtitle {
    margin-top: 0.45rem;
    color: #C9C3C6;
    font-size: 1rem;
}

.badge-row {
    display: flex;
    gap: 9px;
    flex-wrap: wrap;
    margin-top: 0.9rem;
}

.badge {
    display: inline-block;
    padding: 0.28rem 0.62rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    border: 1px solid rgba(196,101,131,0.40);
    background: rgba(109,23,56,0.25);
    color: #F3CFDC;
}

.badge-green {
    border-color: rgba(46,204,113,0.40);
    background: rgba(46,204,113,0.10);
    color: #8AF0B3;
}

.prototype-banner {
    padding: 0.95rem 1rem;
    background:
        linear-gradient(
            90deg,
            rgba(109,23,56,0.38),
            rgba(58,20,36,0.20)
        );
    border: 1px solid #8B1E4B;
    border-left: 5px solid #D94B7A;
    border-radius: 12px;
    color: #F2E7EB;
    margin-bottom: 1.4rem;
}

.section-card {
    padding: 1.2rem;
    border-radius: 16px;
    border: 1px solid rgba(196,101,131,0.25);
    background:
        linear-gradient(
            145deg,
            rgba(23,27,34,0.95),
            rgba(14,17,23,0.95)
        );
    margin-bottom: 1rem;
}

.mini-label {
    color: #D15A84;
    font-weight: 800;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.08em;
    margin-bottom: 0.35rem;
}

.risk-high {
    display: inline-block;
    padding: 0.35rem 0.8rem;
    border-radius: 999px;
    background: rgba(214,48,77,0.18);
    border: 1px solid rgba(214,48,77,0.45);
    color: #FF859A;
    font-weight: 700;
}

.risk-medium {
    display: inline-block;
    padding: 0.35rem 0.8rem;
    border-radius: 999px;
    background: rgba(244,164,64,0.13);
    border: 1px solid rgba(244,164,64,0.35);
    color: #FFC176;
    font-weight: 700;
}

.risk-low {
    display: inline-block;
    padding: 0.35rem 0.8rem;
    border-radius: 999px;
    background: rgba(46,204,113,0.12);
    border: 1px solid rgba(46,204,113,0.35);
    color: #7EE6A8;
    font-weight: 700;
}

.footer-note {
    text-align: center;
    color: #8D858A;
    font-size: 0.82rem;
    margin-top: 2rem;
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# DEFAULT DEMO CONTENT
# =========================================================

DEFAULT_SOURCE = (
    "Patient reports headaches for 3 days. "
    "Patient is allergic to penicillin. "
    "Patient takes metformin 500 mg twice a day. "
    "Blood pressure is 122/78."
)

DEFAULT_TRANSFORMED = DEFAULT_SOURCE


# =========================================================
# SESSION STATE
# =========================================================

if "source_input" not in st.session_state:
    st.session_state["source_input"] = DEFAULT_SOURCE

if "transformed_input" not in st.session_state:
    st.session_state["transformed_input"] = DEFAULT_TRANSFORMED

if "mutation_results" not in st.session_state:
    st.session_state["mutation_results"] = []

if "analysis" not in st.session_state:
    st.session_state["analysis"] = None


# =========================================================
# CALLBACKS
# =========================================================

def clear_analysis():
    st.session_state["analysis"] = None
    st.session_state["mutation_results"] = []


def generate_controlled_drift():
    mutated_text, mutation_results = apply_all_mutations(
        st.session_state["source_input"]
    )

    st.session_state["transformed_input"] = mutated_text
    st.session_state["mutation_results"] = mutation_results
    st.session_state["analysis"] = None


def reset_sample():
    st.session_state["source_input"] = DEFAULT_SOURCE
    st.session_state["transformed_input"] = DEFAULT_TRANSFORMED
    st.session_state["mutation_results"] = []
    st.session_state["analysis"] = None


def run_integrity_analysis():
    source_text = st.session_state["source_input"]
    transformed_text = st.session_state["transformed_input"]

    source_facts = extract_facts(source_text)
    transformed_facts = extract_facts(transformed_text)

    findings = compare_facts(
        source_facts,
        transformed_facts,
    )

    score = integrity_score(findings)

    status = review_status(
        score,
        findings,
    )

    st.session_state["analysis"] = {
        "findings": findings,
        "score": score,
        "status": status,
    }


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        '<div style="padding:0.4rem 0 1.1rem 0;">'
        '<div style="font-size:2rem;font-weight:800;line-height:1;color:#F5F3F4;">'
        'Clin<span style="color:#D94B7A;">Drift</span>'
        '</div>'
        '<div style="margin-top:0.45rem;color:#C9C3C6;font-size:0.82rem;line-height:1.4;">'
        'Clinical Information<br>Integrity Assurance'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown("### Project")

    st.markdown(
        """
**Home**  
Source vs transformed clinical text

**Mutation Lab**  
Controlled integrity testing

**Integrity Check**  
Drift detection and scoring

**Evidence**  
Claim-level traceability

**Audit Report**  
Downloadable JSON report
"""
    )

    st.divider()

    st.markdown(
        '<div class="badge-row">'
        '<span class="badge">v0.1</span>'
        '<span class="badge badge-green">● Research Prototype</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Open source · Transparency first · Human review required"
    )


# =========================================================
# BRANDED HEADER
# =========================================================

st.markdown(
    '<div class="brand-header">'
    '<div class="brand-row">'
    '<div class="logo-mark">'
    '<div class="logo-mark-inner"></div>'
    '</div>'
    '<div>'
    '<div class="brand-title">Clin<span>Drift</span></div>'
    '<div class="brand-subtitle">Clinical Information Integrity Assurance</div>'
    '</div>'
    '</div>'
    '<div class="badge-row">'
    '<span class="badge">v0.1</span>'
    '<span class="badge badge-green">● Research Prototype</span>'
    '<span class="badge">Evidence-based</span>'
    '<span class="badge">Human-centred</span>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="prototype-banner">'
    '<strong>Research prototype only.</strong> '
    'ClinDrift does not diagnose patients, certify AI systems, '
    'or determine regulatory compliance. '
    'Human clinical verification remains required.'
    '</div>',
    unsafe_allow_html=True,
)


# =========================================================
# CLINICAL INFORMATION
# =========================================================

st.markdown("## Clinical information")

left, right = st.columns(2, gap="large")

with left:

    st.markdown(
        '<div class="mini-label">Source record</div>',
        unsafe_allow_html=True,
    )

    st.text_area(
        "Source clinical information",
        key="source_input",
        height=220,
        on_change=clear_analysis,
    )

with right:

    st.markdown(
        '<div class="mini-label">AI / transformed record</div>',
        unsafe_allow_html=True,
    )

    st.text_area(
        "Transformed / AI-generated information",
        key="transformed_input",
        height=220,
        on_change=clear_analysis,
    )


# =========================================================
# MUTATION LAB
# =========================================================

st.divider()

st.markdown("## 🧪 Clinical Drift Mutation Lab")

st.caption(
    "Generate controlled clinical-information errors "
    "to test whether ClinDrift can detect safety-relevant drift."
)

mutation_col, reset_col = st.columns(2)

with mutation_col:

    st.button(
        "Generate controlled drift",
        on_click=generate_controlled_drift,
        width="stretch",
    )

with reset_col:

    st.button(
        "Reset clean sample",
        on_click=reset_sample,
        width="stretch",
    )


# =========================================================
# MUTATION LOG
# =========================================================

mutation_results = st.session_state["mutation_results"]

applied_mutations = [
    result
    for result in mutation_results
    if result.get("applied")
]

if applied_mutations:

    st.markdown("### Injected mutations")

    mutation_df = pd.DataFrame(applied_mutations)

    mutation_df = mutation_df.rename(
        columns={
            "mutation_type": "Mutation type",
            "applied": "Applied",
            "original_value": "Original value",
            "mutated_value": "Mutated value",
        }
    )

    st.dataframe(
        mutation_df,
        width="stretch",
        hide_index=True,
    )

    st.caption(
        "These changes were deliberately introduced "
        "by ClinDrift for controlled integrity testing."
    )


# =========================================================
# INTEGRITY CHECK
# =========================================================

st.divider()

check_left, check_right = st.columns([2, 5])

with check_left:

    st.button(
        "Run integrity check",
        type="primary",
        on_click=run_integrity_analysis,
        width="stretch",
    )

with check_right:

    st.markdown(
        '<div class="section-card">'
        '<div class="mini-label">What happens next</div>'
        'ClinDrift extracts clinical facts, compares the source '
        'and transformed record, assigns severity, calculates '
        'integrity, and links each finding to evidence.'
        '</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# RESULTS
# =========================================================

analysis = st.session_state["analysis"]

if analysis is not None:

    findings = analysis["findings"]
    score = analysis["score"]
    status = analysis["status"]

    critical_count = sum(
        1
        for finding in findings
        if finding.severity == "Critical"
    )

    high_count = sum(
        1
        for finding in findings
        if finding.severity == "High"
    )

    if critical_count > 0 or score < 60:

        risk_level = "High"
        risk_class = "risk-high"

    elif high_count > 0 or score < 85:

        risk_level = "Medium"
        risk_class = "risk-medium"

    else:

        risk_level = "Low"
        risk_class = "risk-low"

    st.divider()

    st.markdown("## Integrity assessment")

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric(
        "Integrity score",
        f"{score}/100",
    )

    metric2.metric(
        "Findings",
        len(findings),
    )

    metric3.metric(
        "Critical findings",
        critical_count,
    )

    with metric4:

        st.markdown(
            '<div style="'
            'background:linear-gradient(145deg,rgba(29,34,43,0.97),rgba(17,20,27,0.97));'
            'border:1px solid rgba(196,101,131,0.27);'
            'border-radius:14px;'
            'padding:1rem;'
            'min-height:125px;">'
            '<div style="color:#C9C3C6;font-size:0.88rem;">Risk level</div>'
            f'<div style="margin-top:1.3rem;"><span class="{risk_class}">'
            f'{risk_level}'
            '</span></div>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("### Review status")

    if findings:

        st.error(
            f"🚨 {status}"
        )

    else:

        st.success(
            f"✅ {status}"
        )

    if findings:

        st.markdown("### Detected drift")

        findings_df = pd.DataFrame(
            [
                finding.to_dict()
                for finding in findings
            ]
        )

        findings_df = findings_df.rename(
            columns={
                "drift_type": "Drift type",
                "severity": "Severity",
                "source_value": "Source value",
                "transformed_value": "Transformed value",
                "source_evidence": "Source evidence",
                "transformed_evidence": "Transformed evidence",
                "rationale": "Why flagged",
            }
        )

        st.dataframe(
            findings_df,
            width="stretch",
            hide_index=True,
        )

        st.markdown("### Evidence traceability")

        st.caption(
            "Every automated flag is linked back "
            "to source and transformed evidence."
        )

        for index, finding in enumerate(
            findings,
            start=1,
        ):

            severity_icon = {
                "Critical": "🔴",
                "High": "🟠",
                "Medium": "🟡",
                "Low": "🟢",
            }.get(
                finding.severity,
                "⚪",
            )

            title = (
                f"{severity_icon} "
                f"{index}. "
                f"{finding.drift_type} "
                f"— {finding.severity}"
            )

            with st.expander(
                title,
                expanded=True,
            ):

                evidence_left, evidence_right = st.columns(2)

                with evidence_left:

                    st.markdown("#### Source")

                    st.write(
                        f"**Value:** {finding.source_value}"
                    )

                    st.info(
                        finding.source_evidence
                    )

                with evidence_right:

                    st.markdown("#### Transformed")

                    st.write(
                        f"**Value:** {finding.transformed_value}"
                    )

                    st.warning(
                        finding.transformed_evidence
                    )

                st.markdown(
                    f"**Why ClinDrift flagged this:** "
                    f"{finding.rationale}"
                )

    else:

        st.success(
            "No drift detected by the current v0.1 rule set."
        )


    # =====================================================
    # MUTATION SELF-TEST
    # =====================================================

    if applied_mutations:

        st.divider()

        st.markdown("## Mutation detection self-test")

        st.caption(
            "Checks whether ClinDrift detected the errors "
            "that the Mutation Lab deliberately introduced."
        )

        expected_types = [
            mutation["mutation_type"]
            for mutation in applied_mutations
        ]

        detected_types = [
            finding.drift_type
            for finding in findings
        ]

        test_rows = []

        detected_count = 0

        for mutation_type in expected_types:

            detected = mutation_type in detected_types

            if detected:
                detected_count += 1

            test_rows.append(
                {
                    "Injected mutation": mutation_type,
                    "Detected by ClinDrift": (
                        "✅ Yes"
                        if detected
                        else "❌ No"
                    ),
                }
            )

        total_mutations = len(expected_types)

        if total_mutations:

            detection_rate = round(
                (
                    detected_count
                    / total_mutations
                )
                * 100
            )

        else:

            detection_rate = 0

        self_left, self_right = st.columns(2)

        self_left.metric(
            "Injected mutations detected",
            f"{detected_count}/{total_mutations}",
        )

        self_right.metric(
            "Detection rate",
            f"{detection_rate}%",
        )

        self_test_df = pd.DataFrame(
            test_rows
        )

        st.dataframe(
            self_test_df,
            width="stretch",
            hide_index=True,
        )

        if detected_count == total_mutations:

            st.success(
                "✅ Self-test passed: ClinDrift detected all "
                "controlled mutations introduced by the Mutation Lab."
            )

        else:

            st.warning(
                "⚠️ Self-test incomplete: one or more "
                "controlled mutations were not detected."
            )


    # =====================================================
    # AUDIT REPORT
    # =====================================================

    st.divider()

    st.markdown("## Audit report")

    report = {
        "project": "ClinDrift",
        "version": "0.1",
        "project_status": "Research Prototype",
        "integrity_score": score,
        "risk_level": risk_level,
        "review_status": status,
        "critical_findings": critical_count,
        "findings": [
            finding.to_dict()
            for finding in findings
        ],
        "controlled_mutations": mutation_results,
        "disclaimer": (
            "ClinDrift is a research and demonstration prototype. "
            "It does not diagnose patients, certify AI systems, "
            "determine regulatory compliance, or replace "
            "human clinical verification."
        ),
    }

    report_json = json.dumps(
        report,
        indent=2,
    )

    report_left, report_right = st.columns([2, 3])

    with report_left:

        st.download_button(
            label="Download integrity report",
            data=report_json,
            file_name="clindrift_integrity_report.json",
            mime="application/json",
            width="stretch",
        )

    with report_right:

        st.markdown(
            '<div class="section-card">'
            '<div class="mini-label">Auditability</div>'
            'The report preserves the integrity score, '
            'findings, severity, evidence and controlled-mutation '
            'record for reproducible evaluation.'
            '</div>',
            unsafe_allow_html=True,
        )


# =========================================================
# RESEARCH PROTOTYPE
# =========================================================

st.divider()

st.markdown("## Research prototype")

purpose_tab, method_tab, limitations_tab = st.tabs(
    [
        "Purpose",
        "Method",
        "Limitations",
    ]
)


with purpose_tab:

    st.markdown(
        """
### Research purpose

ClinDrift investigates a simple question:

> **Did clinically important meaning survive when health information was transformed?**

The prototype focuses on **clinical information integrity**, not diagnosis.

Potential transformation scenarios include:

- AI-generated clinical notes
- clinical summarisation
- GP-to-hospital referrals
- discharge summaries
- patient summaries
- cross-system health-information exchange

ClinDrift is designed as an **independent assurance layer** between source clinical information and transformed output.
"""
    )


with method_tab:

    st.markdown(
        """
### Current v0.1 methodology

ClinDrift performs a lightweight deterministic comparison.

**Current pipeline**

1. Extract supported clinical facts from the source record.
2. Extract equivalent facts from the transformed record.
3. Compare clinically significant values.
4. Detect supported drift classes.
5. Assign a severity level.
6. Link each finding to source evidence.
7. Calculate a transparent integrity score.
8. Require human review when safety-relevant drift is identified.

### Controlled Mutation Lab

The Mutation Lab deliberately introduces known errors into a clean record.

The current prototype can introduce:

- dosage drift
- allergy contradiction
- duration drift

ClinDrift then evaluates whether its own integrity engine detects those controlled mutations.

This creates a basic reproducible evaluation harness rather than relying only on manually selected demonstrations.
"""
    )


with limitations_tab:

    st.markdown(
        """
### Known limitations

ClinDrift v0.1 is intentionally narrow.

It currently demonstrates:

- allergy contradiction detection
- medication dosage drift detection
- symptom-duration drift detection
- evidence traceability
- severity classification
- transparent integrity scoring
- controlled mutation testing
- mutation self-testing
- downloadable audit reporting

It does **not** currently provide:

- medical diagnosis
- treatment recommendations
- comprehensive clinical-language understanding
- production-grade clinical NLP
- hospital or EHR integration
- regulatory certification
- medical-device validation
- proof that an AI-generated record is clinically correct

### Important interpretation

A **100/100 integrity score does not mean the clinical record is medically correct or safe.**

It only means that the current ClinDrift v0.1 rule set did not identify one of the supported forms of information drift.
"""
    )

    st.warning(
        "ClinDrift v0.1 must not be used for clinical decision-making."
    )


# =========================================================
# UK / CANADA RESEARCH CONTEXT
# =========================================================

st.divider()

st.markdown("## UK & Canada research context")

uk_col, canada_col = st.columns(2, gap="large")


with uk_col:

    st.markdown(
        """
### 🇬🇧 United Kingdom

ClinDrift is relevant to research questions involving:

- AI-assisted clinical documentation
- clinical-information summarisation
- human oversight
- information integrity
- evidence traceability
- privacy and AI security
- clinical-safety monitoring

Future versions can provide an assurance mapping against relevant UK digital-health guidance without claiming regulatory compliance.
"""
    )


with canada_col:

    st.markdown(
        """
### 🇨🇦 Canada

ClinDrift is relevant to research questions involving:

- AI-scribe deployment
- interoperable patient summaries
- preservation of clinically important information
- validity and reliability of transformed health information
- privacy and security expectations
- human review
- lifecycle assurance

Future versions can provide a Canadian assurance profile alongside the UK profile.
"""
    )


# =========================================================
# FUTURE RESEARCH ROADMAP
# =========================================================

st.divider()

st.markdown("## Research roadmap")

roadmap1, roadmap2, roadmap3 = st.columns(3)

with roadmap1:

    st.markdown(
        """
### v0.2
**Expanded drift taxonomy**

Planned evaluation of:

- negation drift
- laterality drift
- medication-frequency drift
- measurement drift
- unsupported additions
"""
    )


with roadmap2:

    st.markdown(
        """
### v0.3
**Security assurance**

Planned exploration of:

- prompt-injection contamination
- malicious instruction detection
- source-data manipulation
- privacy leakage indicators
"""
    )


with roadmap3:

    st.markdown(
        """
### Research evaluation
**Benchmarking**

Future work may evaluate:

- precision
- recall
- F1 score
- critical-error detection
- false positives
- mutation detection rate
"""
    )


# =========================================================
# ABOUT
# =========================================================

st.divider()

with st.expander(
    "About ClinDrift v0.1",
    expanded=False,
):

    st.markdown(
        """
**ClinDrift** is an open-source research prototype for detecting safety-relevant semantic drift in transformed clinical information.

### Current capabilities

- Allergy contradiction detection
- Medication dosage drift detection
- Clinical duration drift detection
- Evidence traceability
- Severity classification
- Transparent integrity scoring
- Human-review signalling
- Controlled mutation testing
- Mutation-detection self-testing
- Downloadable JSON audit reports
- UK / Canada research positioning

### Design principles

**Transparent**  
Findings should be explainable.

**Evidence-based**  
Flags should link back to their source evidence.

**Human-centred**  
Automated analysis does not replace clinical verification.

**Security-aware**  
Clinical information integrity is treated as both a patient-safety and cybersecurity concern.
"""
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    '<div class="footer-note">'
    'ClinDrift v0.1 · Open-source research prototype · '
    'Clinical Information Integrity Assurance'
    '</div>',
    unsafe_allow_html=True,
)