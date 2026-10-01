# Filing Guide: Where to Look and What to Look For

Read this when working through a 10-K or 10-Q. The goal is to find what changes an investment view, not to summarize every page.

## Contents
- 10-K item map
- 10-Q differences
- Red flags worth pausing on
- Finding filings on EDGAR

## Completeness checklist

Before research or rating work, confirm each of these was read; `scripts/fetch_filing.py` prints this check. Item 1B is often omitted by companies with nothing to report, and some put the financial statements after Item 15 instead of in Item 8; the script handles both. If one is missing, retry via another EDGAR URL or the company's IR site; if still missing, stop and ask the user to upload the filing.

- **10-K**: Items 1, 1A, 1B, 1C, 2, 3, 5, 7, 7A, 8 (with notes), 9A.
- **10-Q**: Part I Item 1 (financial statements and notes), Item 2 (MD&A), Item 3 (market risk), Item 4 (controls and procedures); Part II Item 1 (legal proceedings), Item 1A (risk factor updates), Item 2 (buybacks), and Items 3-6.

## 10-K item map

| Item | What it contains | What to extract |
|------|------------------|-----------------|
| 1. Business | Products, customers, segments, competition, regulation, employees | How the company makes money, revenue mix by segment and geography, customer concentration, stated competitors |
| 1A. Risk Factors | Risks management is required to disclose | Company-specific risks; anything new or reworded versus last year; risks that are already showing up in the numbers |
| 1B. Unresolved Staff Comments | SEC comments not yet resolved | Rarely populated; if it is, read closely |
| 1C. Cybersecurity | Governance and incident disclosure | Any material incident, board oversight structure |
| 2. Properties | Facilities | Owned vs leased, capacity signals |
| 3. Legal Proceedings | Material litigation | Size of exposure, likelihood, whether reserves exist |
| 5. Market for Equity | Stock info, buybacks, dividends | Repurchase pace and price paid, dividend policy |
| 7. MD&A | Management's explanation of results, liquidity, critical accounting estimates | Drivers of change, non-GAAP reconciliations, liquidity runway, which estimates carry the most judgment |
| 7A. Market Risk | Interest rate, FX, commodity exposure | Sensitivity disclosures |
| 8. Financial Statements | Income statement, balance sheet, cash flow, equity, notes | The numbers, plus the notes (below) |
| 9A. Controls | Internal control assessment | Material weaknesses |
| 10-14. Governance, Comp, Ownership | Often incorporated from the proxy statement | Follow the reference to the DEF 14A |

### Notes to the financials that deserve attention
- **Revenue recognition**: changes in policy, multi-element arrangements, deferred revenue trends
- **Debt**: maturity ladder, covenants, floating vs fixed, refinancing needs
- **Leases**: off-balance-sheet-style obligations now recorded, but still large for retailers and airlines
- **Segment data**: where profits actually come from, which is often different from where revenue comes from
- **Commitments and contingencies**: litigation, purchase obligations, guarantees
- **Income taxes**: effective rate versus statutory, and why
- **Stock-based compensation**: dilution and how much "profit" it consumes
- **Goodwill and intangibles**: impairment history and headroom on recent acquisitions
- **Subsequent events**: things that happened after year end

## 10-Q differences

A 10-Q is unaudited and covers one quarter (plus year-to-date). It has Part I (financial statements, MD&A, market risk, controls) and Part II (legal proceedings, risk factor updates, buybacks, other).

Focus on:
- Year-over-year comparison for the quarter, since seasonality distorts sequential comparisons
- Changes to Risk Factors in Part II, which are often the most informative part
- Liquidity: cash burn, revolver usage, covenant headroom
- Whether the quarter confirms or contradicts the trends in the latest 10-K

Q4 is not filed as a 10-Q; the 10-K covers it, so Q4 results must be derived (full year minus the first three quarters) or taken from the earnings release.

## Red flags worth pausing on

These do not mean "Sell" by themselves. They mean investigate before trusting the headline numbers.

- Revenue growing much faster than operating cash flow, or receivables growing faster than sales
- Rising inventory relative to sales
- Growing gap between GAAP and non-GAAP earnings, or frequent "one-time" charges
- Auditor change, going-concern language, or material weakness in controls
- Restatements or unusual accounting policy changes
- Heavy customer or supplier concentration
- Debt maturities that exceed cash plus realistic free cash flow
- Buybacks funded by debt while free cash flow is flat or falling
- Risk factors that quietly added language about a problem the MD&A does not mention
- Insider selling clustered before weak results (from proxy or Form 4 data)

## Finding filings on EDGAR

- Company search: `https://www.sec.gov/edgar/search/`
- Filing index for a company is reachable by ticker or CIK on the EDGAR search page
- Look for form type `10-K` (annual), `10-Q` (quarterly), `DEF 14A` (proxy statement), `8-K` (current events, including earnings releases)
- Foreign private issuers file `20-F` instead of a 10-K; handle similarly and note the form type in the memo
- Automated requests to sec.gov should identify themselves with a descriptive User-Agent; if fetching directly fails, or any section comes back incomplete, ask the user to upload the filing
