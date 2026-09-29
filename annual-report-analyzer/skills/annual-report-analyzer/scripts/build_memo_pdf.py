#!/usr/bin/env python3
"""Render an investment memo (Markdown with a metadata block) to a formatted PDF.

Usage:
    python build_memo_pdf.py memo.md output.pdf

Requires: reportlab  (pip install reportlab)

Supported syntax is documented in references/memo-structure.md.
"""

import re
import sys
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ---- Palette (edit these to re-theme every memo) ---------------------------
INK = colors.HexColor("#1F2933")
ACCENT = colors.HexColor("#16324F")
MUTED = colors.HexColor("#6B7785")
RULE = colors.HexColor("#D5DAE0")
BAND = colors.HexColor("#F2F5F8")
RATING_COLORS = {
    "buy": colors.HexColor("#1E7B4F"),
    "hold": colors.HexColor("#B7791F"),
    "sell": colors.HexColor("#B83232"),
}

BASE_FONT = "Helvetica"
BOLD_FONT = "Helvetica-Bold"
ITALIC_FONT = "Helvetica-Oblique"

styles = {
    "body": ParagraphStyle(
        "body", fontName=BASE_FONT, fontSize=10, leading=14.5,
        textColor=INK, alignment=TA_JUSTIFY, spaceAfter=7,
    ),
    "h2": ParagraphStyle(
        "h2", fontName=BOLD_FONT, fontSize=14, leading=18,
        textColor=ACCENT, spaceBefore=14, spaceAfter=4,
    ),
    "h3": ParagraphStyle(
        "h3", fontName=BOLD_FONT, fontSize=11, leading=15,
        textColor=ACCENT, spaceBefore=8, spaceAfter=3,
    ),
    "bullet": ParagraphStyle(
        "bullet", parent=None, fontName=BASE_FONT, fontSize=10, leading=14,
        textColor=INK, leftIndent=16, bulletIndent=4, spaceAfter=3,
        alignment=TA_LEFT,
    ),
    "callout": ParagraphStyle(
        "callout", fontName=ITALIC_FONT, fontSize=10, leading=14.5,
        textColor=ACCENT, alignment=TA_LEFT,
    ),
    "cell": ParagraphStyle(
        "cell", fontName=BASE_FONT, fontSize=8.5, leading=11, textColor=INK,
    ),
    "cell_head": ParagraphStyle(
        "cell_head", fontName=BOLD_FONT, fontSize=8.5, leading=11,
        textColor=colors.white,
    ),
    "cover_company": ParagraphStyle(
        "cover_company", fontName=BOLD_FONT, fontSize=22, leading=26,
        textColor=ACCENT,
    ),
    "cover_sub": ParagraphStyle(
        "cover_sub", fontName=BASE_FONT, fontSize=10, leading=14, textColor=MUTED,
    ),
    "meta_label": ParagraphStyle(
        "meta_label", fontName=BOLD_FONT, fontSize=7.5, leading=10,
        textColor=MUTED,
    ),
    "meta_value": ParagraphStyle(
        "meta_value", fontName=BASE_FONT, fontSize=9.5, leading=12, textColor=INK,
    ),
    "badge": ParagraphStyle(
        "badge", fontName=BOLD_FONT, fontSize=16, leading=20,
        textColor=colors.white, alignment=1,
    ),
}


# ---- Inline formatting -----------------------------------------------------
def inline(text: str) -> str:
    """Escape XML then convert **bold** and *italic* to reportlab tags."""
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<i>\1</i>", text)
    return text


# ---- Parsing ---------------------------------------------------------------
def parse_metadata(lines):
    """Return (metadata dict, remaining lines). Metadata is a leading --- block."""
    meta = {}
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                for raw in lines[1:i]:
                    if ":" in raw:
                        k, v = raw.split(":", 1)
                        meta[k.strip().lower()] = v.strip()
                return meta, lines[i + 1:]
    return meta, lines


def is_table_sep(line: str) -> bool:
    return bool(re.match(r"^\s*\|?[\s:\-|]+\|?\s*$", line)) and "-" in line


def split_row(line: str):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def build_table(rows):
    header, body = rows[0], rows[1:]
    ncols = len(header)
    data = [[Paragraph(inline(c), styles["cell_head"]) for c in header]]
    for r in body:
        r = (r + [""] * ncols)[:ncols]
        data.append([Paragraph(inline(c), styles["cell"]) for c in r])

    avail = letter[0] - 1.5 * inch
    first = min(avail * 0.34, 2.4 * inch) if ncols > 2 else avail * 0.4
    rest = (avail - first) / max(ncols - 1, 1)
    t = Table(data, colWidths=[first] + [rest] * (ncols - 1), repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), BAND))
    t.setStyle(TableStyle(style))
    return t


def build_callout(text):
    p = Paragraph(inline(text), styles["callout"])
    t = Table([[p]], colWidths=[letter[0] - 1.5 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BAND),
        ("LINEBEFORE", (0, 0), (0, -1), 3, ACCENT),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


def build_cover(meta):
    width = letter[0] - 1.5 * inch
    company = meta.get("company", "Company")
    ticker = meta.get("ticker", "")
    title = f"{escape(company)}" + (f" ({escape(ticker)})" if ticker else "")

    rating = meta.get("rating", "").strip()
    rating_color = RATING_COLORS.get(rating.lower(), MUTED)
    badge = Table(
        [[Paragraph(escape(rating.upper() or "N/A"), styles["badge"])]],
        colWidths=[1.25 * inch], rowHeights=[0.5 * inch],
    )
    badge.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), rating_color),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    head = Table(
        [[
            [Paragraph(title, styles["cover_company"]),
             Paragraph("Investment Memo", styles["cover_sub"])],
            badge,
        ]],
        colWidths=[width - 1.4 * inch, 1.4 * inch],
    )
    head.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))

    fields = [
        ("FILING", meta.get("filing", "")),
        ("MEMO DATE", meta.get("date", "")),
        ("PRICE", meta.get("price", "")),
        ("VALUE RANGE", meta.get("value_range", "")),
        ("HORIZON", meta.get("horizon", "")),
        ("CONFIDENCE", meta.get("confidence", "")),
    ]
    cells = []
    for label, value in fields:
        cells.append([
            Paragraph(label, styles["meta_label"]),
            Paragraph(escape(value) or "&mdash;", styles["meta_value"]),
        ])
    grid = [cells[0:3], cells[3:6]]
    meta_tbl = Table(grid, colWidths=[width / 3] * 3)
    meta_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BAND),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    return [
        head,
        Spacer(1, 8),
        HRFlowable(width="100%", thickness=1.2, color=ACCENT, spaceAfter=8),
        meta_tbl,
        Spacer(1, 6),
    ]


def parse_body(lines):
    flow = []
    i, n = 0, len(lines)
    para = []

    def flush_para():
        nonlocal para
        if para:
            flow.append(Paragraph(inline(" ".join(para)), styles["body"]))
            para = []

    while i < n:
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            flush_para()
            i += 1
            continue

        if stripped.startswith("# "):  # title is replaced by the cover
            flush_para()
            i += 1
            continue

        if stripped.startswith("### "):
            flush_para()
            flow.append(Paragraph(inline(stripped[4:]), styles["h3"]))
            i += 1
            continue

        if stripped.startswith("## "):
            flush_para()
            flow.append(Paragraph(inline(stripped[3:]), styles["h2"]))
            flow.append(HRFlowable(width="100%", thickness=0.6, color=RULE,
                                   spaceAfter=6))
            i += 1
            continue

        if stripped == "---":
            flush_para()
            flow.append(HRFlowable(width="100%", thickness=0.6, color=RULE,
                                   spaceBefore=4, spaceAfter=6))
            i += 1
            continue

        if stripped.startswith("|"):
            flush_para()
            block = []
            while i < n and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            rows = [split_row(r) for r in block if not is_table_sep(r)]
            if len(rows) >= 1:
                flow.append(build_table(rows))
                flow.append(Spacer(1, 8))
            continue

        if stripped.startswith("> "):
            flush_para()
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            flow.append(KeepTogether([build_callout(" ".join(quote)), Spacer(1, 8)]))
            continue

        if re.match(r"^[-*] ", stripped):
            flush_para()
            flow.append(Paragraph(inline(stripped[2:]), styles["bullet"],
                                  bulletText="\u2022"))
            i += 1
            continue

        para.append(stripped)
        i += 1

    flush_para()
    return flow


# ---- Page furniture --------------------------------------------------------
def make_footer(company, date):
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(BASE_FONT, 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(0.75 * inch, 0.5 * inch,
                          f"{company} | Investment Memo | {date}")
        canvas.drawRightString(letter[0] - 0.75 * inch, 0.5 * inch,
                               f"Page {doc.page}")
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.5)
        canvas.line(0.75 * inch, 0.65 * inch, letter[0] - 0.75 * inch,
                    0.65 * inch)
        canvas.restoreState()
    return footer


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python build_memo_pdf.py memo.md output.pdf")
    src, out = sys.argv[1], sys.argv[2]

    with open(src, encoding="utf-8") as f:
        lines = f.read().splitlines()

    meta, body_lines = parse_metadata(lines)
    company = meta.get("company", "Company")
    date = meta.get("date", "")

    doc = SimpleDocTemplate(
        out, pagesize=letter,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.7 * inch, bottomMargin=0.85 * inch,
        title=f"{company} Investment Memo", author="Annual Report Analyzer",
    )
    story = build_cover(meta) + parse_body(body_lines)
    footer = make_footer(company, date)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
