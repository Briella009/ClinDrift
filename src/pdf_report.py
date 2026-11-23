"""Create a printable audit PDF from the same report data used for JSON export.

Generation is entirely in memory. No report content is written to disk.
"""

from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

import reportlab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    CondPageBreak,
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


INK = colors.HexColor("#20212B")
ACCENT = colors.HexColor("#8D3154")
MUTED = colors.HexColor("#606573")
PALE = colors.HexColor("#F8F3F5")
LINE = colors.HexColor("#DDD6DB")


def _register_fonts():
    """Use fonts bundled with ReportLab so deployment needs no system fonts."""
    font_dir = Path(reportlab.__file__).parent / "fonts"
    if "ClinDriftVera" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("ClinDriftVera", str(font_dir / "Vera.ttf")))
        pdfmetrics.registerFont(TTFont("ClinDriftVeraBold", str(font_dir / "VeraBd.ttf")))
        pdfmetrics.registerFontFamily(
            "ClinDriftVera",
            normal="ClinDriftVera",
            bold="ClinDriftVeraBold",
        )


def _safe(value):
    """Keep report-supplied text as plain text, never ReportLab markup."""
    if value is None or value == "":
        return "Not recorded"
    value = str(value).replace("\r\n", "\n").replace("\r", "\n")
    value = "".join(ch if ch in "\n\t" or ord(ch) >= 32 else " " for ch in value)
    return escape(value).replace("\n", "<br/>")


def _page_decorations(canvas, doc):
    canvas.saveState()
    width, _ = A4
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.6)
    canvas.line(doc.leftMargin, 44, width - doc.rightMargin, 44)
    canvas.setFont("ClinDriftVera", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(doc.leftMargin, 31, "ClinDrift | Research prototype - not for clinical decisions")
    canvas.drawRightString(width - doc.rightMargin, 31, f"Page {doc.page}")
    canvas.restoreState()


def generate_audit_pdf(report):
    """Return PDF bytes for the exact structured report used by JSON download.

    Args:
        report: The dictionary returned by the app's build_report function.
    """
    _register_fonts()
    stream = BytesIO()
    doc = SimpleDocTemplate(
        stream,
        pagesize=A4,
        leftMargin=44,
        rightMargin=44,
        topMargin=48,
        bottomMargin=60,
        title="ClinDrift Integrity Audit Report",
        author="ClinDrift",
        subject="Clinical information integrity research prototype",
    )
    styles = {
        "brand": ParagraphStyle(
            "CD_brand", fontName="ClinDriftVeraBold", fontSize=10,
            leading=13, textColor=ACCENT, spaceAfter=6,
        ),
        "title": ParagraphStyle(
            "CD_title", fontName="ClinDriftVeraBold", fontSize=20,
            leading=26, textColor=INK, spaceAfter=7,
        ),
        "subtitle": ParagraphStyle(
            "CD_subtitle", fontName="ClinDriftVera", fontSize=9,
            leading=14, textColor=MUTED, spaceAfter=17,
        ),
        "heading": ParagraphStyle(
            "CD_heading", fontName="ClinDriftVeraBold", fontSize=11.2,
            leading=15, textColor=ACCENT, spaceBefore=14, spaceAfter=7,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "CD_body", fontName="ClinDriftVera", fontSize=9,
            leading=14.5, textColor=INK, spaceAfter=6,
            splitLongWords=True,
        ),
        "small": ParagraphStyle(
            "CD_small", fontName="ClinDriftVera", fontSize=8,
            leading=12.5, textColor=INK, spaceAfter=4,
            splitLongWords=True,
        ),
        "label": ParagraphStyle(
            "CD_label", fontName="ClinDriftVeraBold", fontSize=8,
            leading=12, textColor=INK,
        ),
        "table": ParagraphStyle(
            "CD_table", fontName="ClinDriftVera", fontSize=8.5,
            leading=12.5, textColor=INK,
            splitLongWords=True,
        ),
    }

    def para(value, style="body"):
        return Paragraph(_safe(value), styles[style])

    def field(label, value):
        return Paragraph(
            f'<font name="ClinDriftVeraBold">{escape(label)}:</font> {_safe(value)}',
            styles["small"],
        )

    story = [
        para("CLINDRIFT", "brand"),
        para("Integrity Audit Report", "title"),
        para("Clinical Information Integrity Assurance | Research prototype", "subtitle"),
        HRFlowable(width="100%", thickness=1.1, color=ACCENT, spaceAfter=14),
        para("Assessment summary", "heading"),
    ]

    summary = [
        ("Integrity score", f'{report.get("integrity_score", "Not recorded")}/100'),
        ("Risk level", report.get("risk_level")),
        ("Human review status", report.get("review_status")),
        ("Source facts extracted", report.get("source_fact_count")),
        ("Transformed facts extracted", report.get("transformed_fact_count")),
        ("Findings", len(report.get("findings") or [])),
        ("Report version", report.get("version")),
        ("Project status", report.get("status")),
    ]
    rows = [[para(label, "label"), para(value, "table")] for label, value in summary]
    table = Table(rows, colWidths=[177, doc.width - 177], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [PALE, colors.white]),
        ("LINEBELOW", (0, 0), (-1, -2), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ("RIGHTPADDING", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(table)

    findings = report.get("findings") or []
    story.append(para(f"Findings ({len(findings)})", "heading"))
    if not findings:
        story.append(para("No drift was detected by the current rule set for this analysis."))
    for index, finding in enumerate(findings, 1):
        story.append(CondPageBreak(100))
        story.append(para(f'{index}. {finding.get("drift_type") or "Finding"}', "heading"))
        story.append(field("Severity", finding.get("severity")))
        story.append(field("Source value", finding.get("source_value")))
        story.append(field("Transformed value", finding.get("transformed_value")))
        story.append(field("Source evidence", finding.get("source_evidence")))
        story.append(field("Transformed evidence", finding.get("transformed_evidence")))
        story.append(field("Reason flagged", finding.get("rationale")))
        story.append(Spacer(1, 3))
        story.append(HRFlowable(width="100%", thickness=0.5, color=LINE))

    mutations = report.get("controlled_mutations") or []
    story.append(CondPageBreak(85))
    story.append(para(f"Controlled mutations ({len(mutations)})", "heading"))
    if not mutations:
        story.append(para("No controlled mutations were recorded for this analysis."))
    for mutation in mutations:
        story.append(CondPageBreak(85))
        story.append(field("Mutation", mutation.get("mutation_type")))
        story.append(field("Applied", "Yes" if mutation.get("applied") else "No"))
        story.append(field("Original value", mutation.get("original_value")))
        story.append(field("Mutated value", mutation.get("mutated_value")))
        story.append(Spacer(1, 5))

    story.append(para("Human review note", "heading"))
    story.append(para(report.get("review_note") or "No reviewer note was recorded."))
    story.append(para("Research use and limitations", "heading"))
    story.append(para(report.get("disclaimer") or (
        "Research prototype only. This report does not diagnose patients or replace "
        "human clinical verification."
    )))
    story.append(para(
        "A high integrity score does not establish clinical correctness. "
        "Unsupported changes may not be detected by this prototype.", "small"
    ))

    doc.build(story, onFirstPage=_page_decorations, onLaterPages=_page_decorations)
    return stream.getvalue()
