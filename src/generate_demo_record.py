"""Synthetic Wisconsin-reduced demo row. Not a medical record or diagnosis."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, Preformatted, SimpleDocTemplate, Spacer

from src.utils import RESEARCH_DISCLAIMER, get_project_root

HIGH_RANGE = """mean perimeter: 122.8
mean concave points: 0.1471
worst radius: 25.38
worst perimeter: 184.6
worst area: 2019.0
worst concave points: 0.2654"""

LOW_RANGE = """mean perimeter: 75.0
mean concave points: 0.02
worst radius: 13.0
worst perimeter: 85.0
worst area: 520.0
worst concave points: 0.07"""

DEMO_NAME = "Ada Example"
DEMO_DOB = "1991-04-02"


def demo_dir() -> Path:
    path = get_project_root() / "demo"
    path.mkdir(exist_ok=True)
    return path


def write_text_files() -> tuple[Path, Path]:
    folder = demo_dir()
    high = folder / "synthetic_wisconsin_reduced_HIGH.txt"
    low = folder / "synthetic_wisconsin_reduced_LOW.txt"
    header = (
        "# SYNTHETIC research row — not a patient, not a diagnosis\n"
        f"# Paste-a-record labels: name={DEMO_NAME}  DOB={DEMO_DOB}\n"
        "# Copy only the field: number lines below into LAKSHYA.\n\n"
    )
    high.write_text(header + HIGH_RANGE + "\n", encoding="utf-8")
    low.write_text(header + LOW_RANGE + "\n", encoding="utf-8")
    return high, low


def write_pdf() -> Path:
    folder = demo_dir()
    path = folder / "synthetic_wisconsin_reduced_demo.pdf"
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "T",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=colors.HexColor("#0a122a"),
        spaceAfter=8,
    )
    warn = ParagraphStyle(
        "W",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#9a3412"),
        leading=13,
        spaceAfter=8,
    )
    body = ParagraphStyle(
        "B",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        spaceAfter=6,
    )
    mono = ParagraphStyle(
        "M",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=10,
        leading=13,
        backColor=colors.HexColor("#f1f5f9"),
        leftIndent=6,
        rightIndent=6,
        spaceBefore=4,
        spaceAfter=10,
    )
    doc = SimpleDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        title="Synthetic Wisconsin reduced research row",
    )
    story = [
        Paragraph("SYNTHETIC research row (live demo)", title),
        Paragraph(RESEARCH_DISCLAIMER, warn),
        Paragraph(
            "This is <b>not</b> a medical report, hospital chart, or diagnosis. "
            "It is a made-up row that matches the <b>wisconsin_reduced</b> schema "
            "(six public FNA-style columns from the sklearn/UCI Wisconsin table). "
            "Do not read symptoms into it. Do not treat the name as a real person.",
            body,
        ),
        Paragraph(f"<b>Demo labels only:</b> {DEMO_NAME} · date of birth {DEMO_DOB}", body),
        Paragraph(
            "In LAKSHYA: Paste a record → Upload text PDF (this file) or paste the HIGH block → "
            "Score this table → Generate locked PDF (name + DOB are labels only, not the password).",
            body,
        ),
        HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=10),
        Paragraph("<b>HIGH-range sample</b> (copy these six lines)", body),
        Preformatted(HIGH_RANGE, mono),
        Paragraph("<b>LOW-range sample</b> (optional second click)", body),
        Preformatted(LOW_RANGE, mono),
        Paragraph(
            "Table: wisconsin_reduced only. Other catalogs are not scored from this sheet.",
            body,
        ),
    ]
    doc.build(story)
    return path


def main() -> None:
    high, low = write_text_files()
    pdf = write_pdf()
    print(high)
    print(low)
    print(pdf)


if __name__ == "__main__":
    main()
