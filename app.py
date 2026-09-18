import json
import pandas as pd
import streamlit as st
from src.extractor import extract_facts
from src.drift_engine import compare_facts
from src.scoring import integrity_score, review_status
from src.mutations import apply_all_mutations

st.set_page_config(page_title="ClinDrift", page_icon="CD", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
.stApp {background:#0E1117;color:#F5F3F4}.block-container{padding-top:1.5rem;padding-bottom:3rem;max-width:1450px}
[data-testid="stSidebar"]{background:#151017;border-right:1px solid #3D2430}h1,h2,h3{letter-spacing:-.02em}p{line-height:1.55}
div.stButton>button,div.stDownloadButton>button{border-radius:10px;min-height:44px;font-weight:700;border:1px solid #A63D63}
[data-testid="stMetric"]{background:#171B22;border:1px solid #3D2430;border-radius:14px;padding:.9rem}
.note{background:#23141B;border:1px solid #6D1738;border-left:5px solid #D94B7A;border-radius:12px;padding:.9rem 1rem}
.mini{font-size:.78rem;text-transform:uppercase;letter-spacing:.08em;color:#D15A84;font-weight:800}
</style>""", unsafe_allow_html=True)

DEFAULT_SOURCE=("Patient reports headaches for 3 days. Patient is allergic to penicillin. "
                "Patient takes metformin 500 mg twice a day. Blood pressure is 122/78.")
DEFAULT_TRANSFORMED=DEFAULT_SOURCE
for key,value in {"source_input":DEFAULT_SOURCE,"transformed_input":DEFAULT_TRANSFORMED,"mutation_results":[],
                  "analysis":None,"review_note":""}.items():
    if key not in st.session_state: st.session_state[key]=value

def clear_analysis(): st.session_state["analysis"]=None

def analyse_current_inputs():
    sf=extract_facts(st.session_state["source_input"]); tf=extract_facts(st.session_state["transformed_input"])
    findings=compare_facts(sf,tf); score=integrity_score(findings)
    st.session_state["analysis"]={"findings":findings,"score":score,"status":review_status(score,findings),
                                  "source_fact_count":len(sf),"transformed_fact_count":len(tf)}

def reset_sample():
    st.session_state["source_input"]=DEFAULT_SOURCE; st.session_state["transformed_input"]=DEFAULT_TRANSFORMED
    st.session_state["mutation_results"]=[]; st.session_state["analysis"]=None; st.session_state["review_note"]=""

def clear_inputs():
    st.session_state["source_input"]=""; st.session_state["transformed_input"]=""; st.session_state["mutation_results"]=[]
    st.session_state["analysis"]=None; st.session_state["review_note"]=""

def generate_controlled_drift():
    if not st.session_state["source_input"].strip(): st.session_state["source_input"]=DEFAULT_SOURCE
    text, results=apply_all_mutations(st.session_state["source_input"])
    st.session_state["transformed_input"]=text; st.session_state["mutation_results"]=results; st.session_state["analysis"]=None

def prepare_presentation_demo(): reset_sample(); generate_controlled_drift(); analyse_current_inputs()

def risk_level(findings,score):
    if any(f.severity=="Critical" for f in findings) or score<60: return "High"
    if any(f.severity=="High" for f in findings) or score<85: return "Medium"
    return "Low"

def build_report():
    a=st.session_state["analysis"]
    if a is None: return None
    return {"project":"ClinDrift","version":"0.1","status":"Research Prototype","integrity_score":a["score"],
            "risk_level":risk_level(a["findings"],a["score"]),"review_status":a["status"],
            "source_fact_count":a["source_fact_count"],"transformed_fact_count":a["transformed_fact_count"],
            "findings":[f.to_dict() for f in a["findings"]], "controlled_mutations":st.session_state["mutation_results"],
            "review_note":st.session_state.get("review_note",""),
            "disclaimer":"Research prototype only. Does not diagnose patients or replace clinical verification."}

with st.sidebar:
    st.markdown("## ClinDrift"); st.caption("Clinical Information Integrity Assurance"); st.markdown("**Research prototype**")
    page=st.radio("Navigate",["Home","Mutation Lab","Integrity Check","Evidence","Audit Report"])
    st.divider(); st.caption("Presentation shortcut")
    st.button("Prepare full demo case",on_click=prepare_presentation_demo,use_container_width=True,
              help="Loads a safe sample, introduces controlled drift, and runs the integrity check.")
    st.caption("Use synthetic, redacted, or explicitly authorised non-confidential data only.")

st.title("ClinDrift"); st.caption("Clinical Information Integrity Assurance")
st.markdown('<div class="note"><strong>Research prototype only.</strong> ClinDrift checks selected forms of information drift. It does not diagnose patients or replace clinical judgement.</div>',unsafe_allow_html=True)
st.write("")

if page=="Home":
    st.header("Home"); st.write("Compare source clinical information with an AI-generated or transformed version. The current prototype provides a transparent deterministic baseline for selected clinical facts.")
    left,right=st.columns(2,gap="large")
    with left:
        st.markdown('<div class="mini">Source record</div>',unsafe_allow_html=True); st.text_area("Source clinical information",key="source_input",height=230,on_change=clear_analysis)
    with right:
        st.markdown('<div class="mini">AI / transformed record</div>',unsafe_allow_html=True); st.text_area("Transformed / AI-generated information",key="transformed_input",height=230,on_change=clear_analysis)
    c1,c2,c3=st.columns(3)
    with c1: st.button("Load clean sample",on_click=reset_sample,use_container_width=True)
    with c2: st.button("Clear inputs",on_click=clear_inputs,use_container_width=True)
    with c3: st.button("Prepare presentation demo",on_click=prepare_presentation_demo,use_container_width=True)
    st.subheader("What the current prototype checks")
    st.markdown("- medication dosage changes\n- allergy contradictions\n- symptom duration changes\n- medication-frequency changes\n- supported measurements and laterality\n- selected omissions and unsupported additions\n- evidence traceability and human-review signalling")

elif page=="Mutation Lab":
    st.header("Clinical Drift Mutation Lab"); st.write("This page deliberately introduces known changes into a safe synthetic sample so the demonstration has reproducible ground truth.")
    st.text_area("Source clinical information",key="source_input",height=200,on_change=clear_analysis)
    c1,c2=st.columns(2)
    with c1: st.button("Generate controlled drift",on_click=generate_controlled_drift,use_container_width=True)
    with c2: st.button("Reset clean sample",on_click=reset_sample,use_container_width=True)
    st.text_area("Transformed / mutated information",key="transformed_input",height=200,on_change=clear_analysis)
    applied=[m for m in st.session_state["mutation_results"] if m.get("applied")]
    if applied:
        st.subheader("Injected mutations"); df=pd.DataFrame(applied).rename(columns={"mutation_type":"Mutation type","applied":"Applied","original_value":"Original value","mutated_value":"Mutated value"}); st.dataframe(df,use_container_width=True,hide_index=True)
    else: st.info("No controlled mutation has been generated in this session yet.")

elif page=="Integrity Check":
    st.header("Integrity Check"); st.write("Run the detector against the source and transformed text currently held in this session.")
    with st.expander("Review the current inputs",expanded=False):
        left,right=st.columns(2)
        with left: st.write("**Source**"); st.write(st.session_state["source_input"] or "No source text supplied.")
        with right: st.write("**Transformed**"); st.write(st.session_state["transformed_input"] or "No transformed text supplied.")
    if not st.session_state["source_input"].strip() or not st.session_state["transformed_input"].strip(): st.warning("Both source and transformed text are required before the integrity check can run.")
    else: st.button("Run integrity check",type="primary",on_click=analyse_current_inputs,use_container_width=True)
    a=st.session_state["analysis"]
    if a is None: st.info("No analysis has been run for the current inputs yet.")
    else:
        findings=a["findings"]; score=a["score"]; critical=sum(1 for f in findings if f.severity=="Critical")
        m1,m2,m3,m4=st.columns(4); m1.metric("Integrity score",f"{score}/100"); m2.metric("Findings",len(findings)); m3.metric("Critical findings",critical); m4.metric("Risk level",risk_level(findings,score))
        if findings:
            st.error(a["status"]); df=pd.DataFrame([{"Drift type":f.drift_type,"Severity":f.severity,"Source value":f.source_value,"Transformed value":f.transformed_value} for f in findings]); st.dataframe(df,use_container_width=True,hide_index=True)
        else: st.success(a["status"])
        applied=[m for m in st.session_state["mutation_results"] if m.get("applied")]
        if applied:
            expected=[m["mutation_type"] for m in applied]; detected=[f.drift_type for f in findings]
            rows=[{"Injected mutation":x,"Detected":"Yes" if x in detected else "No"} for x in expected]
            st.subheader("Controlled self-test"); st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

elif page=="Evidence":
    st.header("Evidence"); a=st.session_state["analysis"]
    if a is None:
        st.info("Run an integrity check first. You can also use 'Prepare full demo case' in the sidebar.")
        if st.session_state["source_input"].strip() and st.session_state["transformed_input"].strip(): st.button("Run integrity check now",on_click=analyse_current_inputs,use_container_width=True)
    else:
        findings=a["findings"]
        if not findings: st.success("No drift was detected by the current rule set for these inputs.")
        else:
            st.write("Each finding is tied back to the exact source and transformed evidence used by the detector.")
            for i,f in enumerate(findings,1):
                with st.expander(f"{i}. {f.drift_type} - {f.severity}",expanded=True):
                    left,right=st.columns(2)
                    with left: st.write("**Source value**"); st.code(f.source_value); st.write("**Source evidence**"); st.info(f.source_evidence)
                    with right: st.write("**Transformed value**"); st.code(f.transformed_value); st.write("**Transformed evidence**"); st.warning(f.transformed_evidence)
                    st.write("**Why it was flagged**"); st.write(f.rationale)
        st.subheader("Human review note"); st.text_area("Reviewer note",key="review_note",height=100,help="Optional note stored in the demonstration audit report.")

elif page=="Audit Report":
    st.header("Audit Report")
    if st.session_state["analysis"] is None:
        st.info("An integrity check must be run before an audit report can be generated.")
        if st.session_state["source_input"].strip() and st.session_state["transformed_input"].strip(): st.button("Run integrity check now",on_click=analyse_current_inputs,use_container_width=True)
    else:
        report=build_report(); st.write("The report preserves the score, findings, evidence, controlled-mutation record and reviewer note.")
        report_json=json.dumps(report,indent=2)
        st.download_button("Download integrity report",data=report_json,file_name="clindrift_integrity_report.json",mime="application/json",use_container_width=True)
        with st.expander("Preview JSON report",expanded=False): st.code(report_json,language="json")

st.divider(); st.caption("ClinDrift v0.1 research prototype. Public demos should use synthetic, redacted, or explicitly authorised non-confidential data only.")
