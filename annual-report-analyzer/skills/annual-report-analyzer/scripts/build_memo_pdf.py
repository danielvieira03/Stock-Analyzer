#!/usr/bin/env python3
"""Render an investment report (Markdown with a metadata block) to a formatted PDF.

Usage:
    python build_memo_pdf.py memo.md output.pdf

Requires: reportlab  (pip install reportlab)

Supported syntax is documented in references/memo-structure.md.
"""

import re
import sys
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ---- Palette (edit these to re-theme every report) -------------------------
INK = colors.HexColor("#1A202C")
NAVY = colors.HexColor("#0B2545")
ACCENT = colors.HexColor("#13315C")
GOLD = colors.HexColor("#B08D3C")
MUTED = colors.HexColor("#667085")
RULE = colors.HexColor("#D5DAE0")
BAND = colors.HexColor("#F3F5F8")
TINT = colors.HexColor("#E6ECF3")
GOOD = colors.HexColor("#1E7B4F")
WARN = colors.HexColor("#B7791F")
BAD = colors.HexColor("#B83232")
NEUTRAL = colors.HexColor("#4A5B73")
RATING_COLORS = {"buy": GOOD, "hold": WARN, "sell": BAD}

BASE_FONT = "Helvetica"
BOLD_FONT = "Helvetica-Bold"
ITALIC_FONT = "Helvetica-Oblique"

PAGE_W, PAGE_H = letter
MARGIN = 0.75 * inch
CONTENT_W = PAGE_W - 2 * MARGIN
BAND_H = 0.95 * inch  # height of the navy header band on page 1

# Built-in PDF fonts lack these glyphs; map them to plain-text equivalents.
GLYPH_MAP = {
    "\u2265": ">=", "\u2264": "<=", "\u2248": "~", "\u2192": "->",
    "\u2190": "<-", "\u2191": "up", "\u2193": "down", "\u2212": "-",
    "\u2713": "yes", "\u2717": "no", "\u25b2": "up", "\u25bc": "down",
}

styles = {
    "body": ParagraphStyle(
        "body", fontName=BASE_FONT, fontSize=9.5, leading=13.8,
        textColor=INK, alignment=TA_LEFT, spaceAfter=6.5,
    ),
    "body_small": ParagraphStyle(
        "body_small", fontName=BASE_FONT, fontSize=8.3, leading=11.6,
        textColor=INK, alignment=TA_LEFT, spaceAfter=5,
    ),
    "h2_num": ParagraphStyle(
        "h2_num", fontName=BOLD_FONT, fontSize=12, leading=15,
        textColor=colors.white, alignment=1,
    ),
    "h2": ParagraphStyle(
        "h2", fontName=BOLD_FONT, fontSize=14.5, leading=18, textColor=NAVY,
    ),
    "h3": ParagraphStyle(
        "h3", fontName=BOLD_FONT, fontSize=10.5, leading=14,
        textColor=ACCENT, spaceBefore=9, spaceAfter=3,
    ),
    "bullet": ParagraphStyle(
        "bullet", fontName=BASE_FONT, fontSize=9.5, leading=13.5,
        textColor=INK, leftIndent=16, bulletIndent=3, spaceAfter=3.5,
        alignment=TA_LEFT, bulletFontName=BOLD_FONT, bulletColor=GOLD,
    ),
    "callout": ParagraphStyle(
        "callout", fontName=ITALIC_FONT, fontSize=9.5, leading=13.8,
        textColor=NAVY, alignment=TA_LEFT,
    ),
    "cell": ParagraphStyle(
        "cell", fontName=BASE_FONT, fontSize=8.3, leading=10.6, textColor=INK,
    ),
    "cell_head": ParagraphStyle(
        "cell_head", fontName=BOLD_FONT, fontSize=8, leading=10.4,
        textColor=colors.white,
    ),
    "tile_label": ParagraphStyle(
        "tile_label", fontName=BOLD_FONT, fontSize=6.8, leading=9,
        textColor=MUTED,
    ),
    "tile_value": ParagraphStyle(
        "tile_value", fontName=BOLD_FONT, fontSize=12, leading=15,
        textColor=NAVY,
    ),
    "tile_note": ParagraphStyle(
        "tile_note", fontName=BASE_FONT, fontSize=6.5, leading=8.2,
        textColor=MUTED,
    ),
    "cover_name": ParagraphStyle(
        "cover_name", fontName=BOLD_FONT, fontSize=24, leading=28,
        textColor=INK,
    ),
    "cover_tagline": ParagraphStyle(
        "cover_tagline", fontName=ITALIC_FONT, fontSize=10.5, leading=14,
        textColor=MUTED, spaceBefore=2, leftIndent=-6,
    ),
    "box_label": ParagraphStyle(
        "box_label", fontName=BOLD_FONT, fontSize=6.8, leading=9,
        textColor=colors.HexColor("#C9D3E0"),
    ),
    "box_value": ParagraphStyle(
        "box_value", fontName=BOLD_FONT, fontSize=13, leading=16,
        textColor=colors.white,
    ),
    "box_rating": ParagraphStyle(
        "box_rating", fontName=BOLD_FONT, fontSize=15, leading=18,
        textColor=colors.white, alignment=1,
    ),
    "info_value": ParagraphStyle(
        "info_value", fontName=BOLD_FONT, fontSize=8.6, leading=11,
        textColor=INK,
    ),
    "source_line": ParagraphStyle(
        "source_line", fontName=BASE_FONT, fontSize=7.8, leading=10.5,
        textColor=MUTED, spaceBefore=6, spaceAfter=4,
    ),
}


# ---- Inline formatting -----------------------------------------------------
def inline(text: str) -> str:
    """Escape XML then convert **bold** and *italic* to reportlab tags."""
    for src, dst in GLYPH_MAP.items():
        text = text.replace(src, dst)
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<i>\1</i>", text)
    return text


def plain(text: str) -> str:
    """Strip markdown emphasis markers for matching logic."""
    return re.sub(r"\*+", "", text).strip()


# ---- Parsing ---------------------------------------------------------------
def parse_metadata(lines):
    """Return (metadata dict, remaining lines). Metadata is a leading --- block."""
    meta = {}
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                for raw in lines[1:i]:
                    if ":" in raw and not raw.lstrip().startswith("#"):
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


# ---- Tables ----------------------------------------------------------------
NUMERIC_RE = re.compile(
    r"^[~\(\-+]?\s*[$\u20ac\u00a3]?\s*[\d][\d,.]*\s*"
    r"(%|x|X|bps|pp|B|M|K|T|bn|mm|tn)?\)?(\s*(to|-)\s*[$]?[\d][\d,.]*\s*"
    r"(%|x|X|B|M|K|T)?)?$"
)
SUMMARY_PREFIXES = ("weighted", "median", "peer median", "peer average", "mean",
                    "average", "total", "consensus")


def is_numeric_cell(text: str) -> bool:
    t = plain(text)
    return bool(t) and len(t) <= 22 and bool(NUMERIC_RE.match(t))


def label_color(text: str, catalyst_mode: bool):
    """Colour for rating / scenario / importance labels, or None."""
    t = plain(text).lower()
    if len(t) > 22:
        return None
    first = t.split()[0] if t.split() else ""
    if first in RATING_COLORS:
        return RATING_COLORS[first]
    if first == "bull":
        return GOOD
    if first == "bear":
        return BAD
    if first == "base":
        return NEUTRAL
    if first in ("high", "medium", "low"):
        if catalyst_mode:
            return {"high": GOOD, "medium": WARN, "low": NEUTRAL}[first]
        return {"high": BAD, "medium": WARN, "low": GOOD}[first]
    return None


def column_widths(rows, ncols):
    """Distribute width by content length, with sensible bounds."""
    weights = []
    for j in range(ncols):
        longest = max(len(plain(r[j])) if j < len(r) else 0 for r in rows)
        weights.append(min(max(longest, 6), 60) ** 0.75)
    total = sum(weights)
    widths = []
    for j in range(ncols):
        words = [w for r in rows if j < len(r) for w in plain(r[j]).split()]
        longest_word = max((stringWidth(w, BOLD_FONT, 8.3) for w in words), default=0)
        min_w = max(0.62 * inch, longest_word + 14)
        widths.append(max(CONTENT_W * weights[j] / total, min_w))
    scale = CONTENT_W / sum(widths)
    return [w * scale for w in widths]


def build_table(rows, catalyst_hint=False):
    header, body = rows[0], rows[1:]
    ncols = len(header)
    catalyst_mode = catalyst_hint or any("catalyst" in h.lower() for h in header)
    body = [(r + [""] * ncols)[:ncols] for r in body]

    numeric = [
        bool(body) and sum(is_numeric_cell(r[j]) for r in body) >= 0.6 * len(body)
        for j in range(ncols)
    ]
    numeric[0] = False

    def align(j):
        return 2 if numeric[j] else 0

    head_cells = []
    for j, c in enumerate(header):
        st = ParagraphStyle(f"hd{j}", parent=styles["cell_head"], alignment=align(j))
        head_cells.append(Paragraph(inline(c), st))
    data = [head_cells]

    summary_rows = []
    for i, r in enumerate(body, start=1):
        is_summary = plain(r[0]).lower().startswith(SUMMARY_PREFIXES)
        if is_summary:
            summary_rows.append(i)
        cells = []
        for j, c in enumerate(r):
            color = label_color(c, catalyst_mode) if j > 0 or ncols == 1 else None
            bold = j == 0 or is_summary or color is not None
            st = ParagraphStyle(
                f"c{i}_{j}", parent=styles["cell"], alignment=align(j),
                fontName=BOLD_FONT if bold else BASE_FONT,
                textColor=color or (NAVY if j == 0 else INK),
            )
            cells.append(Paragraph(inline(c), st))
        data.append(cells)

    t = Table(data, colWidths=column_widths([header] + body, ncols), repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, RULE),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, NAVY),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]
    for i in range(1, len(data)):
        if i in summary_rows:
            style += [("BACKGROUND", (0, i), (-1, i), TINT),
                      ("LINEABOVE", (0, i), (-1, i), 0.9, NAVY)]
        elif i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), BAND))
    t.setStyle(TableStyle(style))
    return t


# ---- Callouts and headings -------------------------------------------------
def build_callout(text):
    p = Paragraph(inline(text), styles["callout"])
    t = Table([[p]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BAND),
        ("LINEBEFORE", (0, 0), (0, -1), 3, GOLD),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def build_heading(number, title):
    box_w = 0.4 * inch
    t = Table(
        [[Paragraph(escape(str(number)), styles["h2_num"]),
          Paragraph(inline(title), styles["h2"])]],
        colWidths=[box_w, CONTENT_W - box_w], rowHeights=[0.36 * inch],
    )
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("RIGHTPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 10),
        ("LINEBELOW", (0, 0), (-1, 0), 1.2, GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    t.keepWithNext = True
    return t


# ---- Page 1 stat tiles -----------------------------------------------------
def split_note(value):
    """'$100.00 (as of 2026-09-28)' -> ('$100.00', 'as of 2026-09-28')."""
    m = re.match(r"^(.*?)\s*\((.*)\)\s*$", value)
    return (m.group(1), m.group(2)) if m else (value, "")


def is_missing(value):
    """True for an empty value or a dash used to mean 'no value'."""
    return value.strip() in ("", "-", "\u2013", "\u2014")


def build_tile_row(fields):
    """Row of label/value tiles. A missing value shows a dash under its label."""
    cells = []
    for label, raw in fields:
        main, note = split_note("" if is_missing(raw) else raw)
        value_style = styles["tile_value"]
        if label.startswith(("UPSIDE", "FROM ATH")) and main:
            color = GOOD if main.startswith("+") else BAD if main.startswith("-") else NAVY
            value_style = ParagraphStyle("tv_up", parent=value_style, textColor=color)
        parts = [Paragraph(label, styles["tile_label"]),
                 Paragraph(escape(main) or "&mdash;", value_style)]
        if note:
            parts.append(Paragraph(escape(note), styles["tile_note"]))
        cells.append(parts)

    t = Table([cells], colWidths=[CONTENT_W / len(cells)] * len(cells))
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BAND),
        ("LINEABOVE", (0, 0), (-1, 0), 2, NAVY),
        ("LINEAFTER", (0, 0), (-2, -1), 0.6, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def build_valuation_strip(meta):
    """The same six metrics on every report. NTM P/E and EV/EBITDA may be a dash
    (a company with negative earnings has no P/E); the other four are required."""
    return build_tile_row([
        ("CURRENT PRICE", meta.get("price", "")),
        ("52-WEEK RANGE", meta.get("week_range", "")),
        ("MARKET CAP", meta.get("market_cap", "")),
        ("NTM P/E", meta.get("ntm_pe", "")),
        ("EV/EBITDA", meta.get("ev_ebitda", "")),
        ("FROM ATH", meta.get("from_ath", "")),
    ])


class Pills(Flowable):
    """Row of rounded pills followed by an optional plain-text label."""

    H = 0.26 * inch
    FONT_SIZE = 8.5
    X0 = -6  # tables overhang the frame padding by 6pt; line up with them

    def __init__(self, pills, label=""):
        super().__init__()
        self.pills, self.label = pills, label  # pills: [(text, fill color)]

    def wrap(self, avail_w, avail_h):
        return avail_w, self.H

    def draw(self):
        c, x = self.canv, self.X0
        for text, fill in self.pills:
            w = stringWidth(text, BOLD_FONT, self.FONT_SIZE) + 18
            c.setFillColor(fill)
            c.roundRect(x, 0, w, self.H, 4, stroke=0, fill=1)
            c.setFillColor(colors.white)
            c.setFont(BOLD_FONT, self.FONT_SIZE)
            c.drawCentredString(x + w / 2, self.H / 2 - 3, text)
            x += w + 8
        if self.label:
            c.setFillColor(MUTED)
            c.setFont(BOLD_FONT, 8.5)
            c.drawString(x + 2, self.H / 2 - 3, self.label.upper())


def build_badges(meta):
    rating = meta.get("rating", "").strip()
    ticker = meta.get("ticker", "").strip()
    sector = meta.get("sector", "").strip()
    pills = []
    if rating:
        pills.append((rating.upper(), RATING_COLORS.get(rating.lower(), MUTED)))
    if ticker:
        pills.append((ticker.upper(), NAVY))
    if not pills and not sector:
        return None
    return Pills(pills, sector)


def build_name_block(meta):
    company = meta.get("company", "Company")
    ticker = meta.get("ticker", "").strip()
    size = 26
    while size > 14 and stringWidth(f"{company}   {ticker}", BOLD_FONT, size) > CONTENT_W:
        size -= 1
    text = f'<font size="{size}">{escape(company)}</font>'
    if ticker:
        muted = "#" + MUTED.hexval()[2:]
        text += (f'&nbsp;&nbsp;<font size="{max(11, round(size * 0.55))}" '
                 f'color="{muted}">{escape(ticker)}</font>')
    style = ParagraphStyle("cover_name_fit", parent=styles["cover_name"],
                           fontSize=size, leading=size + 4, leftIndent=-6)
    flow = [Paragraph(text, style)]
    if meta.get("tagline"):
        flow.append(Paragraph(inline(meta["tagline"]), styles["cover_tagline"]))
    return flow


def build_rating_box(meta):
    """Rating callout, shown on every report."""
    target = meta.get("price_target", "").strip()
    rating = meta.get("rating", "").strip()
    conviction = meta.get("conviction") or meta.get("confidence", "")
    fields = [("PRICE TARGET", target), ("UPSIDE / DOWNSIDE", meta.get("upside", "")),
              ("CONVICTION", conviction)]
    fields = [(label, value) for label, value in fields if value]

    cells, widths = [], []
    if rating:
        cells.append(Paragraph(escape(rating.upper()), styles["box_rating"]))
        widths.append(1.35 * inch)
    rest = (CONTENT_W - sum(widths)) / len(fields)
    for label, raw in fields:
        main, note = split_note(raw)
        parts = [Paragraph(label, styles["box_label"]),
                 Paragraph(escape(main), styles["box_value"])]
        if note:
            parts.append(Paragraph(escape(note), styles["box_label"]))
        cells.append(parts)
        widths.append(rest)

    t = Table([cells], colWidths=widths)
    style = [
        ("BACKGROUND", (0, 0), (-1, -1), ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]
    if rating:
        style += [("BACKGROUND", (0, 0), (0, 0), RATING_COLORS.get(rating.lower(), MUTED)),
                  ("LEFTPADDING", (0, 0), (0, 0), 6), ("RIGHTPADDING", (0, 0), (0, 0), 6)]
    t.setStyle(TableStyle(style))
    return t


def build_info_row(meta):
    """Small row of extra facts at the bottom of the cover; only what is provided."""
    pairs = [("ANALYST", meta.get("analyst", "")),
             ("FY REVENUE EST.", meta.get("fy_revenue", "")),
             ("FY MARGIN EST.", meta.get("fy_margin", "")),
             ("FY EPS EST.", meta.get("fy_eps", "")),
             ("NEXT EARNINGS", meta.get("next_earnings", ""))]
    pairs = [(label, value) for label, value in pairs if value]
    if not pairs:
        return None
    cells = [[Paragraph(label, styles["tile_label"]),
              Paragraph(inline(value), styles["info_value"])] for label, value in pairs]
    t = Table([cells], colWidths=[CONTENT_W / len(cells)] * len(cells))
    t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.6, RULE),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def build_cover(meta):
    flow = [Spacer(1, BAND_H - 0.85 * inch + 0.22 * inch)]
    badges = build_badges(meta)
    if badges:
        flow += [badges, Spacer(1, 9)]
    flow += build_name_block(meta)
    flow += [Spacer(1, 12), build_valuation_strip(meta), Spacer(1, 8),
             build_rating_box(meta)]
    filing = meta.get("filing", "")
    if filing:
        flow.append(Paragraph(f"<b>Source filing:</b> {inline(filing)}",
                              styles["source_line"]))
    else:
        flow.append(Spacer(1, 8))
    info = build_info_row(meta)
    if info:
        flow += [info, Spacer(1, 4)]
    return flow


# Fields every report must have. If one is missing the report is not generated.
REQUIRED_COVER = (
    ("company", "company name"), ("ticker", "ticker"), ("rating", "rating (Buy, Hold or Sell)"),
    ("date", "report date"), ("coverage", "coverage area"),
    ("price", "current price"), ("week_range", "52-week range"),
    ("market_cap", "market cap"), ("from_ath", "change from all-time high"),
    ("price_target", "price target"), ("upside", "upside/downside"),
)


def validate_cover(meta):
    """Exit with a clear message if any required cover field is missing.
    NTM P/E and EV/EBITDA are not required: a missing one shows a dash."""
    missing = [label for key, label in REQUIRED_COVER if is_missing(meta.get(key, ""))]
    if is_missing(meta.get("conviction", "")) and is_missing(meta.get("confidence", "")):
        missing.append("conviction (or confidence)")
    rating = meta.get("rating", "").strip()
    if rating and rating.lower() not in RATING_COLORS:
        missing.append("a rating of exactly Buy, Hold or Sell (got %r)" % rating)
    if missing:
        sys.exit("Cannot generate the report. Missing required cover data: "
                 + "; ".join(missing)
                 + ".\nRetrieve it or ask the user for it; do not render the report without it.")


# ---- Body ------------------------------------------------------------------
def parse_body(lines):
    flow = []
    i, n = 0, len(lines)
    para = []
    section_no = 0
    current_h2 = ""
    current_h3 = ""
    appendix = False

    def body_style():
        return styles["body_small"] if appendix else styles["body"]

    def flush_para():
        nonlocal para
        if para:
            flow.append(Paragraph(inline(" ".join(para)), body_style()))
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
            current_h3 = stripped[4:].strip()
            h3 = Paragraph(inline(current_h3), styles["h3"])
            h3.keepWithNext = True
            flow.append(h3)
            i += 1
            continue

        if stripped.startswith("## "):
            flush_para()
            title = re.sub(r"^\d+[.)]?\s+", "", stripped[3:].strip())
            previous_h2 = current_h2.lower()
            current_h2, current_h3 = title, ""
            appendix = "source" in title.lower() and "methodolog" in title.lower()
            if appendix:
                number = "A"
            else:
                section_no += 1
                number = section_no
            if previous_h2.startswith("executive summary"):
                flow.append(PageBreak())  # page 1 is a one-page snapshot
            else:
                flow.append(Spacer(1, 12))
            flow.append(build_heading(number, title))
            gap = Spacer(1, 6)
            gap.keepWithNext = True
            flow.append(gap)
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
            if rows:
                catalyst_hint = "catalyst" in (current_h3 or current_h2).lower()
                table = build_table(rows, catalyst_hint)
                # Keep the table with its heading / lead-in so neither is stranded.
                lead = []
                if (flow and isinstance(flow[-1], Paragraph)
                        and flow[-1].style.name in ("body", "body_small")):
                    lead.insert(0, flow.pop())
                while flow and getattr(flow[-1], "keepWithNext", False):
                    lead.insert(0, flow.pop())
                if len(rows) <= 14:
                    flow.append(KeepTogether(lead + [table]))
                else:
                    flow.extend(lead + [table])
                flow.append(Spacer(1, 9))
            continue

        if stripped.startswith(">"):
            flush_para()
            quote = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            flow.append(KeepTogether([build_callout(" ".join(quote)), Spacer(1, 9)]))
            continue

        m_num = re.match(r"^(\d+)[.)]\s+(.*)", stripped)
        if re.match(r"^[-*] ", stripped) or m_num:
            flush_para()
            if m_num:
                text, bullet = m_num.group(2), f"{m_num.group(1)}."
            else:
                text, bullet = stripped[2:], "\u2022"
            flow.append(Paragraph(inline(text), styles["bullet"], bulletText=bullet))
            i += 1
            continue

        para.append(stripped)
        i += 1

    flush_para()
    return flow


# ---- Page furniture --------------------------------------------------------
CTX_KEYS = ("company", "ticker", "rating", "date", "coverage")
PAGE_CTX = {k: "" for k in CTX_KEYS}


def draw_first_page(canv, doc):
    """Navy header band: coverage area on the left, report date on the right."""
    ctx = PAGE_CTX
    canv.saveState()
    top = PAGE_H - BAND_H
    canv.setFillColor(NAVY)
    canv.rect(0, top, PAGE_W, BAND_H, stroke=0, fill=1)
    canv.setFillColor(GOLD)
    canv.rect(0, top - 3, PAGE_W, 3, stroke=0, fill=1)

    y = PAGE_H - 0.52 * inch
    if ctx["coverage"]:
        canv.setFillColor(GOLD)
        canv.setFont(BOLD_FONT, 9.5)
        canv.drawString(MARGIN, y, ctx["coverage"].upper())
    if ctx["date"]:
        canv.setFillColor(colors.white)
        canv.setFont(BOLD_FONT, 9.5)
        canv.drawRightString(PAGE_W - MARGIN, y, ctx["date"])
    canv.restoreState()


class NumberedCanvas(rl_canvas.Canvas):
    """Canvas that adds a running header and 'Page X of Y' footer."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_pages = []

    def showPage(self):
        self._saved_pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_pages)
        for state in self._saved_pages:
            self.__dict__.update(state)
            self._draw_furniture(total)
            super().showPage()
        super().save()

    def _draw_furniture(self, total):
        ctx = PAGE_CTX
        page = self._pageNumber
        self.saveState()
        if page > 1:
            name = ctx["company"] + (f" ({ctx['ticker']})" if ctx["ticker"] else "")
            self.setFont(BOLD_FONT, 7.5)
            self.setFillColor(NAVY)
            self.drawString(MARGIN, PAGE_H - 0.5 * inch, name.upper())
            self.setFont(BASE_FONT, 7.5)
            self.setFillColor(MUTED)
            self.drawRightString(PAGE_W - MARGIN, PAGE_H - 0.5 * inch,
                                 "Investment Report")
            self.setStrokeColor(GOLD)
            self.setLineWidth(0.9)
            self.line(MARGIN, PAGE_H - 0.58 * inch, PAGE_W - MARGIN,
                      PAGE_H - 0.58 * inch)
        self.setStrokeColor(RULE)
        self.setLineWidth(0.5)
        self.line(MARGIN, 0.65 * inch, PAGE_W - MARGIN, 0.65 * inch)
        self.setFont(BASE_FONT, 7)
        self.setFillColor(MUTED)
        left = "  |  ".join(x for x in (ctx["company"], ctx["date"]) if x)
        self.drawString(MARGIN, 0.5 * inch, left)
        self.drawCentredString(PAGE_W / 2, 0.5 * inch,
                               "For informational purposes only. Not investment advice.")
        self.drawRightString(PAGE_W - MARGIN, 0.5 * inch, f"Page {page} of {total}")
        self.restoreState()


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: python build_memo_pdf.py memo.md output.pdf")
    src, out = sys.argv[1], sys.argv[2]

    with open(src, encoding="utf-8") as f:
        lines = f.read().splitlines()

    meta, body_lines = parse_metadata(lines)
    validate_cover(meta)
    company = meta.get("company", "Company")
    for key in CTX_KEYS:
        PAGE_CTX[key] = meta.get(key, "").strip()
    PAGE_CTX["company"] = company
    for key in CTX_KEYS:
        PAGE_CTX[key] = re.sub(r"\s+", " ", PAGE_CTX[key])
        for src_g, dst_g in GLYPH_MAP.items():
            PAGE_CTX[key] = PAGE_CTX[key].replace(src_g, dst_g)

    doc = SimpleDocTemplate(
        out, pagesize=letter,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=0.85 * inch, bottomMargin=0.9 * inch,
        title=f"{company} Investment Report", author="Annual Report Analyzer",
    )
    story = build_cover(meta) + parse_body(body_lines)
    doc.build(story, onFirstPage=draw_first_page, canvasmaker=NumberedCanvas)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
