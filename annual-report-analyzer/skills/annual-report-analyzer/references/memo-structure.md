# Report Structure and Markdown Syntax

Every report uses the same sections in the same order, so readers learn where to find things and reports can be compared. Target length: 6-10 pages.

## Contents
- Header block (metadata)
- Section-by-section guide
- Sourcing
- Markdown syntax supported by the PDF builder
- Disclaimer text
- Skeleton

## Header block (metadata)

The report begins with a metadata block the PDF builder turns into the page-1 header band and stat tiles. Use these exact keys:

```
---
company: Apple Inc.
ticker: AAPL
rating: Buy
filing: Form 10-K, fiscal year ended September 28, 2024
date: 2026-09-28
price: $000.00 (as of 2026-09-28)
market_cap: $0.0T
price_target: $000 (12-month, probability-weighted)
upside: +0.0%
value_range: $000 - $000
horizon: 12 months
confidence: Medium
---
```

`rating` must be exactly `Buy`, `Hold`, or `Sell`. The builder colors the rating badge accordingly. `date` is the report date. `price` includes its as-of date in parentheses; text in parentheses is shown as a small note under the value. `price_target` is the probability-weighted price from the Scenario Analysis. `upside` is target versus price, with a sign (`+12.4%` or `-6.0%`). `value_range` is the bear-to-bull span and is shown only if `price_target` is missing. Any missing key shows a dash.

## Section-by-section guide

Section headings are numbered automatically. Write them without numbers. Section 1 sits alone on page 1 with the header band, so keep it to one page.

### 1. Executive Summary
A one-page snapshot. Do not open with the rating. The first paragraph gives the thesis in two or three sentences and the facts that drive it, and ends by stating the rating as the conclusion (for example, "Because of this, we rate the stock Hold"). Then cover the three to five driving facts, the main risk, and the probability-weighted price target versus the current price. Add a small table of headline figures (revenue, growth, margins, free cash flow). A reader who stops here should know what you think and why. Price, market cap, target, and upside appear in the stat tiles, so do not repeat them in a table.

### 2. Company Overview
What the company does, how it makes money, revenue by segment and geography, key products, customers, scale (revenue, employees, market cap), and any recent strategic changes. A segment table is usually worth including.

### 3. Industry Analysis
Market size and growth, structure (fragmented vs concentrated), cycle sensitivity, regulation, secular tailwinds and headwinds, and the forces that determine industry profitability. Draw on web sources; label them.

### 4. Competitive Advantage
Does the company have a durable edge, and is it widening or narrowing? Assess the sources: scale, network effects, switching costs, brand, cost position, intangible assets, regulatory barriers. Name the main competitors qualitatively. Leave the numeric comparison to Peer Analysis (Section 11) and refer to it rather than repeating it. Support claims with evidence such as margins persisting above peers, market share trends, or pricing power.

### 5. Management
Who runs the company, tenure and background, track record against past targets, capital allocation decisions, compensation alignment with shareholders, insider ownership and transactions, and governance (board independence, dual-class shares, related-party dealings). Be candid about strengths and concerns.

Give each of three leaders a `###` subsection, in this order: `### Chief Executive Officer`, `### Chairman`, `### Chief Financial Officer`. In each, name the person and cover tenure and background, track record, pay and ownership alignment, and any concerns. If one person holds two roles (for example CEO and Chairman), say so in both subsections rather than repeating the content, and if a role is vacant or interim, say that. Cover the board and governance in a short paragraph before the subsections.

### 6. Financial Analysis
The core numbers with interpretation. Include a multi-year table (revenue, growth, margins, net income, EPS, FCF, net debt, key ratios), then discuss growth, profitability, cash generation, balance sheet strength, and capital allocation. Note accounting quality issues or non-GAAP adjustments. Valuation multiples versus peers belong in Peer Analysis.

### 7. Recommendation
State the rating in one or two sentences. Then answer the four questions as separate subsections, each with its own `###` subtitle and not as one paragraph: `### Is it a quality business?`, `### Is the trajectory improving?`, `### Is the price attractive?`, `### What is the risk?`. In each, give the answer first, then the reasoning and evidence behind it. Then a compact table with one row per case: **Bull**, **Base**, **Bear**, with columns for probability, price-target range, and the key assumption. The full build is in Section 8; do not repeat its numbers beyond this table. Under a `### What would change our view` subheading, list two or three observable triggers for a more positive view and for a more negative view. End with the confidence level and its main reason.

### 8. Scenario Analysis
One table with a row per case (Bull, Base, Bear) and columns for probability, revenue growth, EPS growth, forward EPS, P/E multiple, and price. Growth targets are next-fiscal-year figures. Price = forward EPS x P/E. Add a final row starting with `Weighted` that shows the probability-weighted values. Probabilities must sum to 100% and the weighted price must equal the sum of probability x price; show that arithmetic in one sentence above the table. The weighted price is the price target.

After the table, add three subsections, `### Bull case`, `### Base case`, and `### Bear case`. Each explains the assumptions behind that case and how they support the thesis: what drives revenue growth, what happens to margins and EPS, why that P/E multiple is justified, and what has to be true in the business or the market for the case to play out. Write two to three paragraphs per case, tied to the filing and the research, so a reader can judge whether the assumptions are reasonable. The summary table in the Recommendation section stays short; the depth lives here.

### 9. Risks and Catalysts
Two ranked tables under `### Top Risks` and `### Top Catalysts` subheadings, each with columns Rank, the item, Why it matters, and a level label (`Level` for risks, `Importance` for catalysts). Levels are exactly `High`, `Medium`, or `Low`, and the builder colors them (for risks High is red; for catalysts High is green). Up to five each, ranked most important first. If fewer than five well-supported items exist, list only those and say so in one sentence. Do not pad. The "Why it matters" cell must be forward-looking, not just a description of what has already happened or is unfolding: explain why the item still matters to the future earnings or valuation, and how it could materialize (the trigger, the mechanism, and where it would show up in the financials or the share price). Keep the cell to two or three sentences. If a risk or catalyst needs more room, follow the table with a short paragraph under it. Include the strongest bear-case argument.

### 10. Wall Street Perspectives
A table of price targets from major banks and brokers found in dated public sources: Firm, Date, Rating, Price target, and a Reason limited to one sentence. Add a final `Consensus` row with the rating split and the mean target. Include only targets you actually found; never invent or estimate a target. If a source is paywalled or unavailable, say so.

### 11. Peer Analysis
A ratios-only table of the company against its three to five main competitors, with columns: P/E, EV/EBITDA, Operating margin, Net margin, FCF margin, Market cap, Revenue growth y/y. Put the subject company first and end with a `Peer median` row. State the as-of date and use consistent definitions across companies (trailing or forward, stated once). After the table, add a short takeaway (two or three sentences) saying where the company sits against the peer median, whether the premium or discount looks justified, and what that implies for the rating. A `> Takeaway:` callout works well.

### 12. Investment Conclusion
One short paragraph: the final take, the rating and target, and the single most important thing to watch.

### Appendix: Sources and Methodology
Shown as lettered section "A" in smaller type. List the filing (form, period, filing date) and each web source with title, publisher, and access date. Note calculation conventions and any significant estimates or data gaps. Finish with the disclaimer.

## Sourcing

Do not use bracketed source tags. Attribute in plain prose, and only when it adds something:

- Refer to the filing by form (10-K, 10-Q, or 20-F) only where it matters, for example when management's narrative and the numbers diverge.
- Name outside sources naturally, such as "according to Reuters" or "per the company's investor presentation".
- Give the date of any market data point (price, multiples, price targets).
- Put the full list of sources, with publisher and access date, in the Sources and Methodology appendix.
- Statements with no attribution are read as the analyst's own judgment.

## Markdown syntax supported by the PDF builder

The builder handles a deliberately small set of syntax so output stays consistent:

- `---` metadata block at the very top (see above)
- `# Title` is ignored in favor of the header band, but may be included for readability
- `## Section heading` (auto-numbered) and `### Subheading`
- Paragraphs separated by blank lines
- `- item` bullet lists and `1. item` numbered lists (use sparingly)
- Pipe tables with a header separator row:
  ```
  | Metric | FY2022 | FY2023 | FY2024 |
  |--------|--------|--------|--------|
  | Revenue ($B) | 394.3 | 383.3 | 391.0 |
  ```
  Numeric columns right-align automatically. Rows starting with `Weighted`, `Median`, `Peer median`, `Average`, `Mean`, `Total`, or `Consensus` are styled as summary rows. Cells reading Buy / Hold / Sell, Bull / Base / Bear, or High / Medium / Low are colored. Tables up to eight columns fit the page.
- `**bold**` and `*italic*` inline
- `> note` for a callout box (good for the key takeaway of a section)
- `---` on its own line after the metadata block inserts a horizontal rule

Avoid raw HTML, images, and nested lists. Use plain text for special characters: the PDF fonts lack glyphs such as >=, ~, and arrows (common ones are converted automatically, but plain ASCII is safest). Ampersands and angle brackets are handled automatically.

## Disclaimer text

Place this as the final paragraph of Sources and Methodology:

> This report is an analytical summary based on public filings and publicly available information as of the date shown. It is for informational purposes only and does not constitute personalized investment advice, an offer, or a solicitation to buy or sell any security. Figures may contain errors or omissions; verify against primary sources before making decisions. Past performance does not guarantee future results.

## Skeleton

```
---
company: 
ticker: 
rating: 
filing: 
date: 
price: 
market_cap: 
price_target: 
upside: 
value_range: 
horizon: 12 months
confidence: 
---

## Executive Summary

## Company Overview

## Industry Analysis

## Competitive Advantage

## Management

### Chief Executive Officer

### Chairman

### Chief Financial Officer

## Financial Analysis

## Recommendation

### Is it a quality business?

### Is the trajectory improving?

### Is the price attractive?

### What is the risk?

### What would change our view

## Scenario Analysis

### Bull case

### Base case

### Bear case

## Risks and Catalysts

### Top Risks

### Top Catalysts

## Wall Street Perspectives

## Peer Analysis

## Investment Conclusion

## Sources and Methodology
```
