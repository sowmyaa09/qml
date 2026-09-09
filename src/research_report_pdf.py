"""Password-locked research score PDF. Not a medical record or diagnosis."""

from __future__ import annotations

import hashlib
import io
import secrets
from datetime import date, datetime, timezone
from typing import Any

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.utils import LONG_DISCLAIMER, RESEARCH_DISCLAIMER

NOT_CLINICAL = "This is not a clinical report, diagnosis, or medical record."

YELLOW = colors.HexColor("#F6E59A")
MAROON = colors.HexColor("#3B0B12")
FIELD_BG = colors.HexColor("#EEF2F6")
INK = colors.HexColor("#111111")
MUTED = colors.HexColor("#4B5563")
PAGE_W, PAGE_H = letter
CONTENT_W = 7.2 * inch


def generate_unlock_key() -> str:
    """Random open-password. Not derived from name or date of birth."""
    return secrets.token_urlsafe(12)


def fingerprint_key(unlock_key: str) -> str:
    return hashlib.sha256(unlock_key.encode("utf-8")).hexdigest()


def score_band(percent: float | None) -> str:
    if percent is None:
        return "—"
    if percent < 35:
        return "Lower"
    if percent < 65:
        return "In the middle"
    return "Higher"


def _friendly_model(name: str) -> str:
    raw = str(name or "")
    if "logistic" in raw.lower():
        return "Linear model"
    if "random forest" in raw.lower():
        return "Tree model"
    if "qsvc" in raw.lower():
        return "Quantum-kernel model"
    if "vqc" in raw.lower():
        return "Quantum circuit model"
    if "rbf" in raw.lower() or "svm" in raw.lower():
        return "Kernel control"
    return raw.replace("_", " ")


def _esc(value: Any) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "doc_title": ParagraphStyle(
            "DocTitle",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=INK,
            spaceBefore=8,
            spaceAfter=14,
            leading=26,
        ),
        "section": ParagraphStyle(
            "SectionBar",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=colors.white,
            leading=14,
        ),
        "label": ParagraphStyle(
            "FieldLabel",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=INK,
            leading=13,
        ),
        "box": ParagraphStyle(
            "FieldBox",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            textColor=INK,
            leading=13,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            textColor=INK,
            leading=14,
            spaceAfter=6,
        ),
        "warn": ParagraphStyle(
            "Warn",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            textColor=colors.HexColor("#9a3412"),
            leading=12,
            spaceAfter=8,
        ),
        "footer": ParagraphStyle(
            "FooterNote",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=MUTED,
            leading=11,
            spaceBefore=10,
        ),
        "right_small": ParagraphStyle(
            "RightSmall",
            parent=base["Normal"],
            fontName="Times-Roman",
            fontSize=8,
            alignment=TA_RIGHT,
            leading=10,
        ),
    }


def _draw_letterhead(canvas, _doc) -> None:
    canvas.saveState()
    canvas.setFillColor(YELLOW)
    canvas.rect(0, PAGE_H - 58, PAGE_W, 58, fill=1, stroke=0)
    canvas.setFillColor(INK)
    canvas.circle(46, PAGE_H - 29, 11, fill=0, stroke=1)
    canvas.setLineWidth(1.1)
    canvas.ellipse(38, PAGE_H - 36, 54, PAGE_H - 22, stroke=1, fill=0)
    canvas.ellipse(40, PAGE_H - 34, 52, PAGE_H - 24, stroke=1, fill=0)
    canvas.setFont("Times-Bold", 20)
    canvas.drawString(64, PAGE_H - 35, "LAKSHYA")
    canvas.setFont("Times-Roman", 8)
    canvas.drawRightString(PAGE_W - 36, PAGE_H - 26, "SIH 2026 · SIH26139")
    canvas.drawRightString(PAGE_W - 36, PAGE_H - 38, "Research prototype — not a hospital")
    canvas.restoreState()


def _section_bar(title: str, styles: dict[str, ParagraphStyle]) -> Table:
    table = Table(
        [[Paragraph(_esc(title), styles["section"])]],
        colWidths=[CONTENT_W],
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), MAROON),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return table


def _value_box(text: str, width: float, styles: dict[str, ParagraphStyle]) -> Table:
    inner = Table(
        [[Paragraph(_esc(text) if str(text).strip() else " ", styles["box"])]],
        colWidths=[width],
    )
    inner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), FIELD_BG),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return inner


def _labeled_box(
    label: str,
    value: str,
    box_width: float,
    styles: dict[str, ParagraphStyle],
    label_width: float = 1.35 * inch,
) -> Table:
    row = Table(
        [
            [
                Paragraph(_esc(label), styles["label"]),
                _value_box(value, box_width, styles),
            ]
        ],
        colWidths=[label_width, box_width],
    )
    row.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return row


def _pair_row(
    left_label: str,
    left_value: str,
    right_label: str,
    right_value: str,
    styles: dict[str, ParagraphStyle],
) -> Table:
    label_w = 1.35 * inch
    gap = 0.2 * inch
    box_w = (CONTENT_W - 2 * label_w - gap) / 2
    pair = Table(
        [
            [
                Paragraph(_esc(left_label), styles["label"]),
                _value_box(left_value, box_w, styles),
                Paragraph(_esc(right_label), styles["label"]),
                _value_box(right_value, box_w, styles),
            ]
        ],
        colWidths=[label_w, box_w, label_w, box_w],
    )
    pair.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (1, 0), 8),
                ("LEFTPADDING", (2, 0), (2, 0), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return pair


def build_plain_pdf(
    *,
    subject_name: str,
    date_of_birth: str,
    catalog_title: str,
    extracted: dict[str, Any],
    result: dict[str, Any],
) -> bytes:
    buf = io.BytesIO()
    styles = _styles()
    issued = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    pct = result.get("research_positive_percent")
    band = score_band(None if pct is None else float(pct))
    hint = (result.get("specialty_hint") or "").strip()
    models = [
        item
        for item in (result.get("models") or [])
        if item.get("percent") is not None
    ]

    if pct is None:
        score_line = "No research score — not enough of this table’s own fields."
        band_line = "No band — no score."
        why_score = (
            "A research score is only produced when this table’s own columns are filled. "
            "Missing fields are not invented from symptoms."
        )
    else:
        score_line = f"{round(float(pct))} / 100 on this public table only."
        band_line = (
            f"{band} research band (Lower / In the middle / Higher). "
            "This buckets the saved model’s score on this teaching file. "
            "It is not a confidence that someone has a disease."
        )
        why_score = (
            "This number exists because the pasted values were aligned to "
            f"{_esc(catalog_title)} and run through saved models trained on that "
            "table’s label. A higher score means the model leans toward that "
            "table’s positive class on this row. It does not identify which "
            "disease a person has, and it does not use a physical exam or lab "
            "order from a clinic."
        )

    why_not_diagnosis = (
        "LAKSHYA cannot be sure — and does not claim — that this is “the disease "
        "you got.” Each model only sees one public table’s columns. There is no "
        "fused diagnosis, no symptom checker, and no personal clinical workup. "
        "Treat the score as a research ranking on a benchmark file, then see a "
        "licensed clinician for personal care. We do not name doctors."
    )

    findings_bits = [score_line]
    if hint:
        findings_bits.append(
            "Domain hint (not a referral, not a ranking of doctors): " + hint
        )
    for item in models:
        findings_bits.append(
            f"{_friendly_model(item.get('name') or '')}: "
            f"{round(float(item['percent']))} / 100"
        )
    filled = [(k, v) for k, v in (extracted or {}).items() if v is not None and v != ""]
    if filled:
        findings_bits.append(
            "Numbers used: "
            + "; ".join(f"{name}={value}" for name, value in filled[:20])
        )
    findings_text = " ".join(findings_bits)

    story: list = [
        Spacer(1, 8),
        Paragraph("Research Score Sheet", styles["doc_title"]),
        Paragraph(RESEARCH_DISCLAIMER, styles["warn"]),
        Paragraph(LONG_DISCLAIMER, styles["body"]),
        Paragraph(NOT_CLINICAL, styles["body"]),
        Spacer(1, 4),
        KeepTogether(
            [
                _section_bar("Administrative Details", styles),
                Spacer(1, 8),
                _labeled_box(
                    "Subject name:",
                    f"{subject_name} (label only)",
                    CONTENT_W - 1.35 * inch,
                    styles,
                ),
                _pair_row(
                    "Date of birth:",
                    f"{date_of_birth} (label only)",
                    "Sex / gender:",
                    "Not collected",
                    styles,
                ),
                _labeled_box(
                    "Public table:",
                    catalog_title,
                    CONTENT_W - 1.35 * inch,
                    styles,
                ),
                _pair_row(
                    "Issued:",
                    issued,
                    "Received from:",
                    "LAKSHYA research UI",
                    styles,
                ),
                Spacer(1, 12),
            ]
        ),
        KeepTogether(
            [
                _section_bar("Prototype credentials", styles),
                Spacer(1, 8),
                _labeled_box(
                    "Platform name:",
                    "LAKSHYA",
                    CONTENT_W - 1.35 * inch,
                    styles,
                ),
                _pair_row(
                    "Prepared by:",
                    "Q-Care Detect software",
                    "Role:",
                    "Not a treating clinician",
                    styles,
                ),
                Spacer(1, 6),
                Paragraph(
                    "This sheet was generated by <b>LAKSHYA</b>, an educational hybrid "
                    "quantum–classical research prototype (SIH 2026 SIH26139). "
                    "LAKSHYA is not a hospital and does not employ or rank doctors. "
                    f"Name {_esc(subject_name)} and date of birth {_esc(date_of_birth)} "
                    "are labels on this file only. We do not name doctors.",
                    styles["body"],
                ),
                Spacer(1, 8),
            ]
        ),
        KeepTogether(
            [
                _section_bar("Purpose and Scope", styles),
                Spacer(1, 8),
                Paragraph(
                    "This report has been prepared as a <b>research risk classification</b> "
                    f"on one public teaching table (<i>{_esc(catalog_title)}</i>). "
                    "It is not an insurance report, not a treatment plan, and not a diagnosis. "
                    "Saved models only see this table’s columns and label. "
                    "There is no fused multi-disease answer for a person.",
                    styles["body"],
                ),
                Spacer(1, 8),
            ]
        ),
        KeepTogether(
            [
                _section_bar("Research findings", styles),
                Spacer(1, 8),
                _labeled_box(
                    "Research score:",
                    score_line,
                    CONTENT_W - 1.35 * inch,
                    styles,
                ),
                _labeled_box(
                    "Research band:",
                    band_line,
                    CONTENT_W - 1.35 * inch,
                    styles,
                ),
                Spacer(1, 8),
                Table(
                    [
                        [
                            Paragraph(
                                "Score and numbers used",
                                styles["label"],
                            ),
                            _value_box(findings_text, 5.2 * inch, styles),
                        ]
                    ],
                    colWidths=[2.0 * inch, 5.2 * inch],
                ),
                Spacer(1, 12),
            ]
        ),
        KeepTogether(
            [
                _section_bar("How to read this number (not a diagnosis)", styles),
                Spacer(1, 8),
                Paragraph(why_score, styles["body"]),
                Paragraph(why_not_diagnosis, styles["body"]),
                Spacer(1, 8),
            ]
        ),
        Paragraph(
            "Note: Unlock this file with the generated key shown in the app. "
            "Name and date of birth are not the password. "
            "LAKSHYA is a research prototype, not an AI care partner or medical device.",
            styles["footer"],
        ),
    ]

    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.95 * inch,
        bottomMargin=0.65 * inch,
        title="LAKSHYA research score sheet",
        author="LAKSHYA",
    )
    doc.build(story, onFirstPage=_draw_letterhead, onLaterPages=_draw_letterhead)
    return buf.getvalue()


def encrypt_pdf(plain_pdf: bytes, unlock_key: str) -> bytes:
    reader = PdfReader(io.BytesIO(plain_pdf))
    writer = PdfWriter()
    writer.append(reader)
    writer.encrypt(user_password=unlock_key, owner_password=unlock_key)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


def build_locked_pdf(
    *,
    subject_name: str,
    date_of_birth: str | date,
    catalog_title: str,
    extracted: dict[str, Any],
    result: dict[str, Any],
    unlock_key: str | None = None,
) -> tuple[bytes, str]:
    key = unlock_key or generate_unlock_key()
    dob = (
        date_of_birth.isoformat()
        if isinstance(date_of_birth, date)
        else str(date_of_birth)
    )
    plain = build_plain_pdf(
        subject_name=subject_name.strip(),
        date_of_birth=dob,
        catalog_title=catalog_title,
        extracted=extracted,
        result=result,
    )
    locked = encrypt_pdf(plain, key)
    return locked, key
