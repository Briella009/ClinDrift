"""Audit exported PDF text to ensure actual report values are preserved."""

from io import BytesIO
from pypdf import PdfReader

from src.pdf_report import generate_audit_pdf


def sample_report():
    return {
        "project": "ClinDrift",
        "version": "0.1",
        "status": "Research Prototype",
        "integrity_score": 54,
        "risk_level": "High",
        "review_status": "Human review required",
        "source_fact_count": 4,
        "transformed_fact_count": 4,
        "findings": [{
            "drift_type": "Dosage drift",
            "severity": "Critical",
            "source_value": "500 mg",
            "transformed_value": "1000 mg",
            "source_evidence": "Patient takes metformin 500 mg twice a day.",
            "transformed_evidence": "Patient takes metformin 1000 mg twice a day.",
            "rationale": "The dosage value changed during transformation.",
        }],
        "controlled_mutations": [{
            "mutation_type": "Dosage drift",
            "applied": True,
            "original_value": "500 mg",
            "mutated_value": "1000 mg",
        }],
        "review_note": "Reviewer requests clinical verification of the dose.",
        "disclaimer": "Research prototype only; not a medical device.",
    }


def to_pdf_text(report):
    blob = generate_audit_pdf(report)
    assert blob.startswith(b"%PDF-")
    assert blob.rstrip().endswith(b"%%EOF")
    pages = PdfReader(BytesIO(blob)).pages
    return pages, "\n".join(page.extract_text() or "" for page in pages)


def test_pdf_contains_real_findings_and_reviewer_note():
    report = sample_report()
    pages, text = to_pdf_text(report)
    assert len(pages) >= 1
    for expected in (
        "Integrity Audit Report", "Integrity score", "54/100",
        "Human review required", "Dosage drift", "Critical",
        "500 mg", "1000 mg", "Source evidence", "Transformed evidence",
        "Patient takes metformin", "Controlled mutations",
        "Human review note", report["review_note"], report["disclaimer"],
    ):
        assert expected in text, expected


def test_pdf_handles_empty_report_and_escaped_note():
    report = sample_report()
    report["findings"] = []
    report["controlled_mutations"] = []
    report["review_note"] = "Special note: <approved> & not markup."
    _, text = to_pdf_text(report)
    assert "No drift was detected" in text
    assert "No controlled mutations were recorded" in text
    assert "<approved> & not markup." in text


def test_long_note_not_truncated_in_pdf():
    report = sample_report()
    report["review_note"] = "Detailed note ABC123. " * 750
    pages, text = to_pdf_text(report)
    assert len(pages) >= 3
    assert text.count("Detailed note ABC123.") >= 700
    assert "Research use and limitations" in text
