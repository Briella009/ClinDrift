"""Basic checks for in-memory PDF audit report generation."""

from src.pdf_report import generate_audit_pdf


def sample_report():
    return {
        "project": "ClinDrift",
        "version": "0.1",
        "status": "Research Prototype",
        "integrity_score": 54,
        "risk_level": "High",
        "review_status": "Human review required",
        "source_fact_count": 3,
        "transformed_fact_count": 3,
        "findings": [
            {
                "drift_type": "Dosage drift",
                "severity": "Critical",
                "source_value": "500 mg",
                "transformed_value": "1000 mg",
                "source_evidence": "Source <clinical> & text",
                "transformed_evidence": "Transformed > text",
                "rationale": "Dosage changed during transformation.",
            }
        ],
        "controlled_mutations": [
            {
                "mutation_type": "Dosage drift",
                "applied": True,
                "original_value": "500 mg",
                "mutated_value": "1000 mg",
            }
        ],
        "review_note": "Needs human verification.",
        "disclaimer": "Research prototype only.",
    }


def test_pdf_report_generates_with_findings():
    pdf = generate_audit_pdf(sample_report())
    assert pdf.startswith(b"%PDF-")
    assert len(pdf) > 2000
    assert pdf.rstrip().endswith(b"%%EOF")


def test_pdf_report_handles_empty_findings_and_long_untrusted_notes():
    report = sample_report()
    report["findings"] = []
    report["controlled_mutations"] = []
    report["review_note"] = "<script>alert('x')</script> & " + ("Review note. " * 1500)
    pdf = generate_audit_pdf(report)
    assert pdf.startswith(b"%PDF-")
    assert len(pdf) > 2000
