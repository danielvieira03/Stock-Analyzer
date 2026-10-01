#!/usr/bin/env python3
"""Download a 10-K or 10-Q from SEC EDGAR (or load a local file), split it into
Items, and check that every required section is present.

Why this exists: a 10-K is often 500,000+ characters of text, and web-fetch
tools silently cut long pages short, so late sections (controls, legal
proceedings) go missing. This script saves the whole filing to disk and splits
it so each Item can be read on its own.

Usage:
    python fetch_filing.py FSLR --form 10-K --out filing_FSLR
    python fetch_filing.py LULU --form 10-Q --out filing_LULU
    python fetch_filing.py --file uploaded_filing.htm --form 10-K --out filing_x

Set SEC_USER_AGENT to "Your Name your@email.com" (SEC asks for this).

Output directory: full.txt, one file per section (item_1A.txt, part2_item_1.txt,
...), and manifest.json. Exit code 0 if every required section was found,
2 if any is missing or too short, 1 on download/parse failure.
Standard library only (a .pdf input needs the `pdftotext` command).
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
import urllib.request

UA = os.environ.get(
    "SEC_USER_AGENT", "annual-report-analyzer-skill (set SEC_USER_AGENT to your name and email)"
)

# (key, title regex, required, min chars)
TENK = [
    ("1", r"Business", True, 500),
    ("1A", r"Risk\s+Factors", True, 500),
    ("1B", r"Unresolved\s+Staff\s+Comments", False, 4),
    ("1C", r"Cybersecurity", False, 100),
    ("2", r"Properties", True, 20),
    ("3", r"Legal\s+Proceedings", True, 20),
    ("4", r"Mine\s+Safety\s+Disclosures?", False, 4),
    ("5", r"Market\s+for\s+(?:the\s+)?(?:Registrant|Company|Our)", True, 100),
    ("6", r"(?:\[?Reserved\]?|Selected\s+(?:Consolidated\s+)?Financial\s+Data)", False, 0),
    ("7", r"Management.{0,3}s\s+Discussion", True, 1000),
    ("7A", r"Quantitative\s+and\s+Qualitative", True, 50),
    ("8", r"(?:Consolidated\s+)?Financial\s+Statements", True, 1000),
    ("9", r"Changes\s+in\s+and\s+Disagreements", False, 4),
    ("9A", r"Controls\s+and\s+Procedures", True, 200),
    ("9B", r"Other\s+Information", False, 4),
    ("9C", r"Disclosure\s+Regarding\s+Foreign", False, 4),
    ("10", r"Directors", False, 20),
    ("11", r"Executive\s+Compensation", False, 20),
    ("12", r"Security\s+Ownership", False, 20),
    ("13", r"Certain\s+Relationships", False, 20),
    ("14", r"Principal\s+Account", False, 20),
    ("15", r"Exhibits?", False, 20),
    ("16", r"Form\s+10-K\s+Summary", False, 0),
]
TENQ_P1 = [
    ("1", r"(?:Condensed\s+)?(?:Consolidated\s+)?Financial\s+Statements", True, 1000),
    ("2", r"Management.{0,3}s\s+Discussion", True, 1000),
    ("3", r"Quantitative\s+and\s+Qualitative", True, 50),
    ("4", r"Controls\s+and\s+Procedures", True, 200),
]
TENQ_P2 = [
    ("1", r"Legal\s+Proceedings", True, 20),
    ("1A", r"Risk\s+Factors", True, 20),
    ("2", r"Unregistered\s+Sales", True, 20),
    ("3", r"Defaults\s+Upon", False, 4),
    ("4", r"Mine\s+Safety", False, 4),
    ("5", r"Other\s+Information", False, 4),
    ("6", r"Exhibits?", False, 20),
]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def find_filing(ident, form):
    """Return (url, filing_date, period) of the latest filing of this form."""
    ident = ident.strip()
    if ident.isdigit():
        cik = int(ident)
    else:
        tickers = json.loads(fetch("https://www.sec.gov/files/company_tickers.json"))
        match = [v for v in tickers.values() if v["ticker"].upper() == ident.upper()]
        if not match:
            sys.exit("Ticker %s not found on EDGAR. Use the CIK number instead." % ident)
        cik = match[0]["cik_str"]
    sub = json.loads(fetch("https://data.sec.gov/submissions/CIK%010d.json" % cik))
    rec = sub["filings"]["recent"]
    for i, f in enumerate(rec["form"]):
        if f == form:
            acc = rec["accessionNumber"][i].replace("-", "")
            url = "https://www.sec.gov/Archives/edgar/data/%d/%s/%s" % (cik, acc, rec["primaryDocument"][i])
            return url, rec["filingDate"][i], rec["reportDate"][i]
    sys.exit("No %s found in the recent filings for %s." % (form, ident))


def html_to_text(raw):
    s = raw.decode("utf-8", errors="ignore")
    s = re.sub(r"(?is)<ix:header>.*?</ix:header>", " ", s)  # hidden XBRL block
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?i)</(td|th)>", " | ", s)
    s = re.sub(r"(?i)</(p|div|tr|h[1-6]|li|table)>|<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"(?:\|\s*)+\|", "|", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s*\n\s*", "\n", s)
    return s.strip()


def load_text(path):
    if path.lower().endswith(".pdf"):
        out = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True)
        if out.returncode != 0:
            sys.exit("pdftotext failed or is not installed; convert the PDF to text first.")
        return out.stdout.decode("utf-8", errors="ignore")
    raw = open(path, "rb").read()
    return html_to_text(raw) if b"<" in raw[:5000] else raw.decode("utf-8", errors="ignore")


def heading_candidates(text, items):
    """Positions of each item heading that starts a line, as {key: [positions]}."""
    cands = {}
    for key, title, _, _ in items:
        rx = re.compile(r"(?im)^[\s|]*Item\s*%s\s*[\.\:\-\u2013\u2014|]*\s*%s" % (re.escape(key), title))
        cands[key] = [m.start() for m in rx.finditer(text)]
    return cands


def split_items(text, items):
    """Return {key: text}. Missing items are absent.

    Each heading shows up twice (table of contents, then the body), so working
    backwards from the end, take the last heading that sits before the next
    item's heading. That picks the body copy even for one-line sections such
    as "Item 1B. None.".
    """
    cands = heading_candidates(text, items)
    chosen, bound = {}, len(text)
    for key, *_ in reversed(items):
        before = [p for p in cands[key] if p < bound]
        if before:
            chosen[key] = bound = before[-1]
    marks = sorted((p, k) for k, p in chosen.items())
    out = {}
    for i, (pos, key) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        out[key] = text[pos:end].strip()
    return out


def check(sections, items, form="10-K"):
    rows, ok = [], True
    for key, _, required, minlen in items:
        n = len(sections.get(key, ""))
        if key == "8" and form == "10-K" and n < minlen and "Consolidated Balance Sheets" in sections.get("15", ""):
            # some companies place the financial statements after Item 15 (F-pages)
            rows.append((key, required, len(sections["15"]), "OK (in Item 15)"))
            continue
        status = "OK" if n >= minlen and key in sections else ("MISSING" if key not in sections else "SHORT")
        if status != "OK" and required:
            ok = False
        rows.append((key, required, n, status))
    return rows, ok


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("company", nargs="?", help="ticker or CIK")
    ap.add_argument("--form", choices=["10-K", "10-Q"], default="10-K")
    ap.add_argument("--file", help="use a local .htm/.txt/.pdf instead of downloading")
    ap.add_argument("--out", default="filing", help="output directory")
    a = ap.parse_args()
    if not a.company and not a.file:
        ap.error("give a ticker/CIK or --file")

    meta = {"form": a.form}
    try:
        if a.file:
            text = load_text(a.file)
            meta["source"] = a.file
        else:
            url, fdate, period = find_filing(a.company, a.form)
            meta.update(source=url, filing_date=fdate, period_end=period)
            text = html_to_text(fetch(url))
    except Exception as e:  # network, HTTP 403/429, parse
        print("FAILED to get the filing: %s" % e, file=sys.stderr)
        print("Ask the user to upload the filing.", file=sys.stderr)
        return 1

    os.makedirs(a.out, exist_ok=True)
    open(os.path.join(a.out, "full.txt"), "w").write(text)

    results, ok = {}, True
    if a.form == "10-K":
        secs = split_items(text, TENK)
        groups = [("", TENK, secs)]
    else:
        i = [m.start() for m in re.finditer(r"(?im)^[\s|]*PART\s+II\s*[\.\-–—|]*\s*OTHER\s+INFORMATION", text)]
        cut = i[-1] if i else len(text)
        groups = [
            ("part1_", TENQ_P1, split_items(text[:cut], TENQ_P1)),
            ("part2_", TENQ_P2, split_items(text[cut:], TENQ_P2)),
        ]
    print("%s | %s | %d characters total" % (meta["form"], meta.get("source", ""), len(text)))
    print("%-12s %-9s %9s  %s" % ("Section", "Required", "Chars", "Status"))
    for prefix, items, secs in groups:
        rows, g_ok = check(secs, items, a.form)
        ok &= g_ok
        for key, required, n, status in rows:
            name = "%sItem %s" % (prefix.replace("_", " ").title().replace("Part", "Part ") if prefix else "", key)
            print("%-12s %-9s %9d  %s" % (name.strip(), "yes" if required else "no", n, status))
            if key in secs:
                open(os.path.join(a.out, "%sitem_%s.txt" % (prefix, key)), "w").write(secs[key])
            results[prefix + key] = {"required": required, "chars": n, "status": status}
    meta["sections"] = results
    meta["complete"] = ok
    json.dump(meta, open(os.path.join(a.out, "manifest.json"), "w"), indent=2)
    print("\nComplete: %s. Files written to %s/" % ("YES" if ok else "NO", a.out))
    if not ok:
        print("A required section is missing or too short. Check full.txt for it directly; "
              "if it is truly absent, ask the user to upload the filing.")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
