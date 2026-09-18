import json

import pandas as pd
import streamlit as st

from src.drift_engine import compare_facts
from src.extractor import extract_facts
from src.mutations import apply_all_mutations
from src.scoring import integrity_score, review_status


st.set_page_config(
    page_title="ClinDrift",
    page_icon="CD",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
.stApp {background:#0E1117;color:#F5F3F4}
.block-container{padding-top:1.5rem;padding-bottom:3rem;max-width:1450px}
[data-testid="stSidebar"]{background:#151017;border-right:1px solid #3D2430}
h1,h2,h3{letter-spacing:-.02em}
p{line-height:1.55}
div.stButton>button,div.stDownloadButton>button{
    border-radius:10px;min-height:44px;font-weight:700;border:1px solid #A63D63
}
[data-testid="stMetric"]{
    background:#171B22;border:1px solid #3D2430;border-radius:14px;padding:.9rem
}
.note{
    background:#23141B;border:1px solid #6D1738;border-left:5px solid #D94B7A;
    border-radius:12px;padding:.9rem 1rem
}
.mini{
    font-size:.78rem;text-transform:uppercase;letter-spacing:.08em;
    color:#D15A84;font-weight:800
}
</style>
""",
    unsafe_allow_html=True,
)


DEFAULT_SOURCE = (
    "Patient reports headaches for 3 days. "
    "Patient is allergic to penicillin. "
    "Patient takes metformin 500 mg twice a day. "
    "Blood pressure is 122/78."
)

STATE_DEFAULTS = {
    "source_record": DEFAULT_SOURCE,
    "transformed_record": DEFAULT_SOURCE,
    "mutation_results": [],
    "analysis": None,
    "review_note_record": "",
}

for key, value in STATE_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def _sync_visible_text_widgets():
    """Keep page-specific widget mirrors aligned with persistent record state."""
    for key in ("home_source", "mutation_source"):
        if key in st.session_state:
            st.session_state[key] = st.session_state["source_record"]

    for key in ("home_transformed", "mutation_transformed"):
        if key in st.session_state:
            st.session_state[key] = st.session_state["transformed_record"]

    if "evidence_review_note" in st.session_state:
        st.session_state["evidence_review_note"] = st.session_state["review_note_record"]


def sync_home_inputs():
    st.session_state["source_record"] = st.session_state.get(
        "home_source", st.session_state["source_record"]
    )
    st.session_state["transformed_record"] = st.session_state.get(
        "home_transformed", st.session_state["transformed_record"]
    )
    st.session_state["analysis"] = None


def sync_mutation_inputs():
    st.session_state["source_record"] = st.session_state.get(
        "mutation_source", st.session_state["source_record"]
    )
    st.session_state["transformed_record"] = st.session_state.get(
        "mutation_transformed", st.session_state["transformed_record"]
    )
    st.session_state["analysis"] = None


def sync_review_note():
    st.session_state["review_note_record"] = st.session_state.get(
        "evidence_review_note", ""
    )


def analyse_current_inputs():
    source_text = st.session_state.get("source_record", DEFAULT_SOURCE)
    transformed_text = st.session_state.get("transformed_record", source_text)

    source_facts = extract_facts(source_text)
    transformed_facts = extract_facts(transformed_text)
    findings = compare_facts(source_facts, transformed_facts)
    score = integrity_score(findings)

    st.session_state["analysis"] = {
        "findings": findings,
        "score": score,
        "status": review_status(score, findings),
        "source_fact_count": len(source_facts),
        "transformed_fact_count": len(transformed_facts),
    }


def reset_sample():
    st.session_state["source_record"] = DEFAULT_SOURCE
    st.session_state["transformed_record"] = DEFAULT_SOURCE
    st.session_state["mutation_results"] = []
    st.session_state["analysis"] = None
    st.session_state["review_note_record"] = ""
    _sync_visible_text_widgets()


def clear_inputs():
    st.session_state["source_record"] = ""
    st.session_state["transformed_record"] = ""
    st.session_state["mutation_results"] = []
    st.session_state["analysis"] = None
    st.session_state["review_note_record"] = ""
    _sync_visible_text_widgets()


def generate_controlled_drift():
    source_text = st.session_state.get("source_record", "").strip()
    if not source_text:
        source_text = DEFAULT_SOURCE
        st.session_state["source_record"] = source_text

    mutated_text, results = apply_all_mutations(source_text)
    st.session_state["transformed_record"] = mutated_text
    st.session_state["mutation_results"] = results
    st.session_state["analysis"] = None
    _sync_visible_text_widgets()


def prepare_presentation_demo():
    reset_sample()
    generate_controlled_drift()
    analyse_current_inputs()


def risk_level(findings, score):
    if any(f.severity == "Critical" for f in findings) or score < 60:
        return "High"
    if any(f.severity == "High" for f in findings) or score < 85:
        return "Medium"
    return "Low"


def build_report():
    analysis = st.session_state.get("analysis")
    if analysis is None:
        return None

    return {
        "project": "ClinDrift",
        "version": "0.1",
        "status": "Research Prototype",
        "integrity_score": analysis["score"],
        "risk_level": risk_level(analysis["findings"], analysis["score"]),
        "review_status": analysis["status"],
        "source_fact_count": analysis["source_fact_count"],
        "transformed_fact_count": analysis["transformed_fact_count"],
        "findings": [f.to_dict() for f in analysis["findings"]],
        "controlled_mutations": st.session_state.get("mutation_results", []),
        "review_note": st.session_state.get("review_note_record", ""),
        "disclaimer": (
            "Research prototype only. Does not diagnose patients or replace "
            "clinical verification."
        ),
    }


with st.sidebar:
    st.markdown("## ClinDrift")
    st.caption("Clinical Information Integrity Assurance")
    st.markdown("**Research prototype**")

    page = st.radio(
        "Navigate",
        ["Home", "Mutation Lab", "Integrity Check", "Evidence", "Audit Report"],
    )

    st.divider()
    st.caption("Presentation shortcut")
    st.button(
        "Prepare full demo case",
        on_click=prepare_presentation_demo,
        width="stretch",
        help=(
            "Loads a safe sample, introduces controlled drift, and runs "
            "the integrity check."
        ),
    )
    st.caption(
        "Use synthetic, redacted, or explicitly authorised non-confidential data only."
    )


st.title("ClinDrift")
st.caption("Clinical Information Integrity Assurance")
st.markdown(
    '<div class="note"><strong>Research prototype only.</strong> '
    "ClinDrift checks selected forms of information drift. It does not diagnose "
    "patients or replace clinical judgement.</div>",
    unsafe_allow_html=True,
)
st.write("")


if page == "Home":
    st.header("Home")
    st.write(
        "Compare source clinical information with an AI-generated or transformed "
        "version. The current prototype provides a transparent deterministic "
        "baseline for selected clinical facts."
    )

    st.session_state.setdefault("home_source", st.session_state["source_record"])
    st.session_state.setdefault(
        "home_transformed", st.session_state["transformed_record"]
    )

    left, right = st.columns(2, gap="large")
    with left:
        st.markdown(
            '<div class="mini">Source record</div>', unsafe_allow_html=True
        )
        st.text_area(
            "Source clinical information",
            key="home_source",
            height=230,
            on_change=sync_home_inputs,
        )

    with right:
        st.markdown(
            '<div class="mini">AI / transformed record</div>',
            unsafe_allow_html=True,
        )
        st.text_area(
            "Transformed / AI-generated information",
            key="home_transformed",
            height=230,
            on_change=sync_home_inputs,
        )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.button(
            "Load clean sample",
            on_click=reset_sample,
            width="stretch",
        )
    with c2:
        st.button(
            "Clear inputs",
            on_click=clear_inputs,
            width="stretch",
        )
    with c3:
        st.button(
            "Prepare presentation demo",
            on_click=prepare_presentation_demo,
            width="stretch",
        )

    st.subheader("What the current prototype checks")
    st.markdown(
        "- medication dosage changes\n"
        "- allergy contradictions\n"
        "- symptom duration changes\n"
        "- medication-frequency changes\n"
        "- supported measurements and laterality\n"
        "- selected omissions and unsupported additions\n"
        "- evidence traceability and human-review signalling"
    )


elif page == "Mutation Lab":
    st.header("Clinical Drift Mutation Lab")
    st.write(
        "This page deliberately introduces known changes into a safe synthetic "
        "sample so the demonstration has reproducible ground truth."
    )

    st.session_state.setdefault(
        "mutation_source", st.session_state["source_record"]
    )
    st.session_state.setdefault(
        "mutation_transformed", st.session_state["transformed_record"]
    )

    st.text_area(
        "Source clinical information",
        key="mutation_source",
        height=200,
        on_change=sync_mutation_inputs,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.button(
            "Generate controlled drift",
            on_click=generate_controlled_drift,
            width="stretch",
        )
    with c2:
        st.button(
            "Reset clean sample",
            on_click=reset_sample,
            width="stretch",
        )

    st.text_area(
        "Transformed / mutated information",
        key="mutation_transformed",
        height=200,
        on_change=sync_mutation_inputs,
    )

    applied = [
        m for m in st.session_state.get("mutation_results", []) if m.get("applied")
    ]
    if applied:
        st.subheader("Injected mutations")
        mutation_df = pd.DataFrame(applied).rename(
            columns={
                "mutation_type": "Mutation type",
                "applied": "Applied",
                "original_value": "Original value",
                "mutated_value": "Mutated value",
            }
        )
        st.dataframe(mutation_df, width="stretch", hide_index=True)
    else:
        st.info("No controlled mutation has been generated in this session yet.")


elif page == "Integrity Check":
    st.header("Integrity Check")
    st.write(
        "Run the detector against the source and transformed text currently held "
        "in this session."
    )

    source_record = st.session_state.get("source_record", "")
    transformed_record = st.session_state.get("transformed_record", "")

    with st.expander("Review the current inputs", expanded=False):
        left, right = st.columns(2)
        with left:
            st.write("**Source**")
            st.write(source_record or "No source text supplied.")
        with right:
            st.write("**Transformed**")
            st.write(transformed_record or "No transformed text supplied.")

    if not source_record.strip() or not transformed_record.strip():
        st.warning(
            "Both source and transformed text are required before the integrity "
            "check can run."
        )
    else:
        st.button(
            "Run integrity check",
            type="primary",
            on_click=analyse_current_inputs,
            width="stretch",
        )

    analysis = st.session_state.get("analysis")
    if analysis is None:
        st.info("No analysis has been run for the current inputs yet.")
    else:
        findings = analysis["findings"]
        score = analysis["score"]
        critical = sum(1 for f in findings if f.severity == "Critical")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Integrity score", f"{score}/100")
        m2.metric("Findings", len(findings))
        m3.metric("Critical findings", critical)
        m4.metric("Risk level", risk_level(findings, score))

        if findings:
            st.error(analysis["status"])
            findings_df = pd.DataFrame(
                [
                    {
                        "Drift type": f.drift_type,
                        "Severity": f.severity,
                        "Source value": f.source_value,
                        "Transformed value": f.transformed_value,
                    }
                    for f in findings
                ]
            )
            st.dataframe(findings_df, width="stretch", hide_index=True)
        else:
            st.success(analysis["status"])

        applied = [
            m
            for m in st.session_state.get("mutation_results", [])
            if m.get("applied")
        ]
        if applied:
            expected = [m["mutation_type"] for m in applied]
            detected = [f.drift_type for f in findings]
            rows = [
                {
                    "Injected mutation": mutation_type,
                    "Detected": "Yes" if mutation_type in detected else "No",
                }
                for mutation_type in expected
            ]
            st.subheader("Controlled self-test")
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


elif page == "Evidence":
    st.header("Evidence")
    analysis = st.session_state.get("analysis")

    if analysis is None:
        st.info(
            "Run an integrity check first. You can also use 'Prepare full demo "
            "case' in the sidebar."
        )
        if (
            st.session_state.get("source_record", "").strip()
            and st.session_state.get("transformed_record", "").strip()
        ):
            st.button(
                "Run integrity check now",
                on_click=analyse_current_inputs,
                width="stretch",
            )
    else:
        findings = analysis["findings"]

        if not findings:
            st.success(
                "No drift was detected by the current rule set for these inputs."
            )
        else:
            st.write(
                "Each finding is tied back to the exact source and transformed "
                "evidence used by the detector."
            )

            for index, finding in enumerate(findings, 1):
                with st.expander(
                    f"{index}. {finding.drift_type} - {finding.severity}",
                    expanded=True,
                ):
                    left, right = st.columns(2)

                    with left:
                        st.write("**Source value**")
                        st.code(finding.source_value)
                        st.write("**Source evidence**")
                        st.info(finding.source_evidence)

                    with right:
                        st.write("**Transformed value**")
                        st.code(finding.transformed_value)
                        st.write("**Transformed evidence**")
                        st.warning(finding.transformed_evidence)

                    st.write("**Why it was flagged**")
                    st.write(finding.rationale)

        st.subheader("Human review note")
        st.session_state.setdefault(
            "evidence_review_note", st.session_state["review_note_record"]
        )
        st.text_area(
            "Reviewer note",
            key="evidence_review_note",
            height=100,
            on_change=sync_review_note,
            help="Optional note stored in the demonstration audit report.",
        )


elif page == "Audit Report":
    st.header("Audit Report")

    if st.session_state.get("analysis") is None:
        st.info(
            "An integrity check must be run before an audit report can be generated."
        )
        if (
            st.session_state.get("source_record", "").strip()
            and st.session_state.get("transformed_record", "").strip()
        ):
            st.button(
                "Run integrity check now",
                on_click=analyse_current_inputs,
                width="stretch",
            )
    else:
        report = build_report()
        st.write(
            "The report preserves the score, findings, evidence, "
            "controlled-mutation record and reviewer note."
        )
        report_json = json.dumps(report, indent=2)

        st.download_button(
            "Download integrity report",
            data=report_json,
            file_name="clindrift_integrity_report.json",
            mime="application/json",
            width="stretch",
        )

        with st.expander("Preview JSON report", expanded=False):
            st.code(report_json, language="json")


st.divider()
st.caption(
    "ClinDrift v0.1 research prototype. Public demos should use synthetic, "
    "redacted, or explicitly authorised non-confidential data only."
)
